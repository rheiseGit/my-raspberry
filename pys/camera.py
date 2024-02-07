"""
This modull should provide classes providing access to a camera.
"""

import cv2
import numpy as np

try:
    import picamera2
except Exception as e:
    picamera2 = None

import base64
import time
from collections import deque, OrderedDict
import pys.transformer as transformer
from threading import Thread


class AdapterOpenCV:
    """Adapter indented to access camera on PC and provide interface used by CameraController"""

    def __init__(self):
        """Encapsulates Object 'OpenCV VideoCapture'"""
        #: cv2.VideoCapture: Provides access to camera
        self.vc = cv2.VideoCapture(0)
        # reading image from camera in order to determine size of the image taken
        _, img = self.vc.read()
        h, w, _ = img.shape
        #: tuple: Size of Image (height,width)
        self.__imagesize = (h, w)

    def get_configs(self) -> dict:
        """Returns description of configurations of the camera

        Returns:
            dict: configurations
        """
        return {}

    def read(self) -> np.array:
        """Returns image in BGR colorspace

        Returns:
            np.array: Image
        """
        success, image = self.vc.read()
        return image

    def get_imagesize(self) -> tuple:
        """Returns size of images provides by the camera

        Returns:
            tuple: height, width
        """
        return self.__imagesize

    def release(self):
        """Releases camera"""
        self.vc.release()

    def check(self) -> bool:
        """checks if camera if available

        Returns:
            bool: True if camera is available and does not return None
        """
        if self.vc is None or not self.vc.isOpened():
            return False
        else:
            return True


class AdapterPiCamera:
    """Adapter indented to access camera on RPI-OS (Bullseye or higher) and provide interface used by CameraController"""

    def __init__(self, resolution=(160, 120)):
        """Encapsulates Object Picamera2

        Args:
            resolution (tuple, optional): Image size (width,heiht)
        """
        #: picamera.Picamera2: provides access to camera on RPi
        self.__pc = picamera2.Picamera2()
        #: tuple: image size aks resolution
        self.__imagesize = None

        if isinstance(resolution, int) and resolution in range(
            len(self.__pc.sensor_modes)
        ):
            # choice of resolution based on sensor mode
            sensor_mode_index = resolution
            self.__imagesize = self.__pc.sensor_modes[sensor_mode_index]["size"]
            sensor_dict = dict(
                output_size=self.__imagesize,
                bit_depth=self.__pc.sensor_modes[sensor_mode_index]["bit_depth"],
            )
        else:
            # choice of resolution based on given size (wight,height)
            sensor_dict = {}
            if isinstance(resolution, tuple) and len(resolution) == 2:
                self.__imagesize = resolution
            else:
                self.__imagesize = resolution = (160, 120)

        #: dict: camera configuration set to Picamera2
        self.__camera_config = self.__pc.create_still_configuration(
            main=dict(size=self.__imagesize),
            lores={},
            sensor=sensor_dict,
        )
        self.__pc.configure(self.__camera_config)
        self.__pc.start()

    def get_imagesize(self):
        """Returns image size

        Returns:
            tuple: image size (width,height)
        """
        return self.__imagesize

    def get_configs(self):
        """Returns configurations received from Picamera2

        Returns:
            dict: configuration
        """
        return str(self.__pc.camera_configuration())

    def read(self) -> np.array:
        """Returns image in BGR colorspace

        Returns:
            np.array: Image
        """
        image = self.__pc.capture_array("main")
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return image

    def release(self):
        """Releases camera"""
        self.__pc.stop()
        self.__pc.close()

    def check(self):
        """Checks if camera is available

        Returns:
            bool: True if camera is available
        """
        try:
            _ = self.read()
            return True
        except RuntimeError:
            return False


def bgr_to_grayscale_bgr(img) -> np.array:
    """Converts image form colorspace BGR to grayscale in colorspace BGR

    Args:
        img (np.array): image BGR

    Returns:
        np.array: image BGR grayscale
    """
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img


class CameraController(object):
    def __init__(self, adapter):
        #:Adapter: allows to access to camera via specified interface
        self.__adapter = adapter
        #: int: counts images taken
        self.__counter = 0
        #: bool: indictes that thread is running
        self.__running = False
        # CommerController allows to keep transformation which can be applied to an image
        # __basic_transformations are implemented in this class and intended to be applied first
        # __registered_transformation are implemented elsewhere
        # __post_transformations are intended to be applied last, after resizing of image!
        #:dict: contains function which allow to transform an image
        self.__transformations = {
            "post": OrderedDict(
                {
                    "info": self.__add_info_to_frame,
                }
            ),
            "basic": OrderedDict(
                {
                    "vflip": lambda img: cv2.flip(img, 1),
                    "hflip": lambda img: cv2.flip(img, 0),
                    "gray": lambda img: bgr_to_grayscale_bgr(img),
                }
            ),
            "registered": OrderedDict(
                {
                    "smooth": transformer.Smoother(0.6),
                    "test": transformer.Test(1),
                    "delta": transformer.SimpleMotionDetect(),
                }
            ),
        }
        #:dict: indicate which transformation are active
        self.__active_transformations = dict(
            basic=["vflip", "hflip"], registered=[], post=[]
        )
        #:cv2.FONT: font to be used for text incerted to an img
        self.__font = cv2.FONT_HERSHEY_SIMPLEX
        #:deque: keeps track of time neccesary to apply transformations
        self.__times = deque([], 10)
        #:np.array: last frame taken by the camera
        self._last_frame = None
        #:np.array:last frame taken by the camera with basic and registered transformatinos applied
        self._last_frame_br = None
        #:np.array:last frame taken by tha woth all tranformations applied
        self._last_frame_brp = None

    def get_active_transformations(self, key) -> list:
        """Returns list of active transformations

        Args:
            key (str): 'basic', 'registered' or 'post'

        Returns:
            list: list of keys of active transformation
        """
        return list(self.__active_transformations[key])

    def set_active_transformations(self, key, transformations):
        """Activates transformations

        Args:
            key (str): 'basic', 'registered' or 'post'
            transformations (list): contains ids of transformation
        """
        self.__active_transformations[key] = set(transformations)

    def get_keys_of_transformations(self, key):
        return list(self.__transformations[key].keys())

    def get_transformation(self, key_group, key):
        return self.__transformations[key_group][key]

    def release(self):
        """Releases camera"""
        self.__adapter.release()

    def single_run_get_frame(self) -> np.array:
        """Reads image, applies transformations and return result

        Returns:
            np.array: image
        """
        self.__counter += 1
        starttime = time.time()
        try:
            image = self.__adapter.read()
        except Exception as e:
            image = np.ones((10, 10, 3))
        if image is None:
            image = np.ones((10, 10, 3))
        self._last_frame = image.copy()
        image = self.__apply_transformations("basic", image)
        self._last_frame_br = self.__apply_transformations("registered", image)
        self._last_frame_brp = self.__apply_transformations("post", self._last_frame_br)
        self.__times.append(time.time() - starttime)
        return image

    def __apply_transformations(self, key, image) -> np.array:
        """Applies all active transformation of a given key to an image and returns the result

        Args:
            key (str): 'basic', 'registered' or 'post'
            image (np.array): image to be transformed

        Returns:
            np.array: transformed image
        """
        try:
            for transformation in self.__transformations[key].keys():
                if transformation in self.__active_transformations[key]:
                    image = self.__transformations[key][transformation](image)
        except Exception as e:
            print(e)
        return image

    def __thread_func(self):
        """Read image and apllies transformation"""
        self.__running = True
        while self.__running:
            self.single_run_get_frame()

    def run(self):
        """Wrappes __thread_func"""
        thread = Thread(target=self.__thread_func, args=())
        thread.start()

    def stop(self):
        """Stoppes thread started by run"""
        self.__running = False

    def running(self) -> bool:
        """Retruns running state of object"""
        return self.__running

    def __make_stream_default_image(self):
        """Returns an default image"""
        img = np.ones((120, 160, 3)) * 50
        img = cv2.putText(
            img,
            "Camera not running",
            (10, 60),
            self.__font,
            0.4,
            # (0, 0, 0),
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
        return img

    def get_stream_frame_as_bytes(self) -> bytes:
        """Returns last frame encoded as byte

        Returns:
            bytes: encoded image
        """
        if self.__running and self._last_frame_br is not None:
            frame = cv2.resize(
                self._last_frame_br, (160, 120), interpolation=cv2.INTER_LINEAR
            )
            frame = self.__apply_transformations("post", frame)
            _, jpeg = cv2.imencode(".jpg", frame)
            self.__last_transformed_frame_as_bytes = jpeg.tobytes()
        elif not hasattr(self, "__last_transformed_frame_as_bytes"):
            frame = self.__make_stream_default_image()
            _, jpeg = cv2.imencode(".jpg", frame)
            self.__last_transformed_frame_as_bytes = jpeg.tobytes()
        return self.__last_transformed_frame_as_bytes

    def get_last_frame(self) -> np.array:
        """Returns last frame without transformations applied.
            If camera is not running reads returns new frame

        Returns:
            np.array: last frame without transformations applied
        """
        if not self.running():
            return self.single_run_get_frame()
        return self._last_frame

    def get_last_transformed_frame(self):
        """Retruns last frame with transformations applied.
            If camera is not running reads returns new frame.

        Returns:
            np.array: last frame with transformations applied
        """
        if not self.running():
            return self.single_run_get_frame()
        return self._last_frame_brp

    def get_and_store_last_transformed_frame(self):
        self.__image = self.get_last_transformed_frame()
        return self.__image

    def __add_info_to_frame(self, frame) -> np.array:
        """adds some written textual information to the image

        Args:
            frame (np.array): image to add info into

        Returns:
            np.array: image with info
        """
        time_ms = sum(self.__times) / len(self.__times) * 1000
        return cv2.putText(
            frame,
            f"{round(time_ms,3)} ms",
            (10, 19),
            self.__font,
            0.5,
            # (0, 0, 0),
            (0, 255, 255),
            1,
            cv2.LINE_AA,
        )

    def save_stored_image_to_file(self, filepath) -> None:
        """Saves image to file

        Args:
            filepath (_type_): _description_
        """
        cv2.imwrite(filepath, self.__image)

    def check(self) -> bool:
        """Checks if camera if available

        Returns:
            bool: True if camera is available
        """
        return self.__adapter.check()

    def get_size(self) -> tuple:
        """Returns image size used

        Returns:
            tuple: width,height
        """
        return self.__adapter.get_imagesize()


def encode_frame_as_jpg(frame) -> bytes:
    """Provides encodes image as ???

    Args:
        frame (_type_): _description_

    Returns:
        bytes: _description_
    """
    _, buffer = cv2.imencode(".jpg", frame)
    dataURI = "data:image/jpeg;base64, " + base64.b64encode(buffer.tobytes()).decode(
        "ascii"
    )
    return dataURI


def gen(camera: CameraController):
    """Returns Generator for streaming video

    Args:
        camera (CameraController): _description_

    Yields:
        byte: ???
    """
    while True:
        frame = camera.get_stream_frame_as_bytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")


if __name__ == "__main__":
    cam = CameraController()
    res, img = cam.video.read()
    print(res, type(img))
