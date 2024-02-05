import cv2
import numpy as np
import picamera2
import base64
import time
from collections import deque, OrderedDict
import pys.transformer as transformer
from threading import Thread

CAMERA_INDEX = -1
print("CAMERA")
print(" - Camera-Index", CAMERA_INDEX)


class AdapterOpenCV:
    def __init__(self):
        self.vc = cv2.VideoCapture(-1)

    def get_configs(self):
        return "???"

    def read(self) -> np.array:
        success, image = self.vc.read()
        return image

    def read_high_resolution(self):
        return self.read()

    def release(self):
        self.vc.release()

    def check(self) -> bool:
        """check if camera if available

        Returns:
            bool: True means that camera is available
        """
        if self.vc is None or not self.vc.isOpened():
            return False
        else:
            return True


class AdapterPiCamera:
    """Adapter indented to be used on Raspberry-Pi-OS (Bullseye or higher)
    Provides interface to class CameraController
    """

    def __init__(self, resolution=(160, 120)):
        self.__pc = picamera2.Picamera2()
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

        self.__video_config = self.__pc.create_still_configuration(
            main=dict(size=self.__imagesize),
            lores={},
            sensor=sensor_dict,
        )
        self.__pc.configure(self.__video_config)
        self.__pc.start()

    def get_imagesize(self):
        return self.__imagesize

    def get_configs(self):
        """returns configuration of picamera"""
        return str(self.__pc.camera_configuration())

    def read(self) -> np.array:
        image = self.__pc.capture_array("main")
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return image

    def release(self):
        self.__pc.stop()
        self.__pc.close()

    def check(self):
        try:
            _ = self.read()
            return True
        except RuntimeError:
            return False


def bgr_to_grayscale_bgr(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img


class CameraController(object):
    def __init__(self, adapter):
        self.__adapter = adapter
        self.__counter = 0
        self.__font = cv2.FONT_HERSHEY_SIMPLEX
        self.__running = False
        # __basic_transformations are implemented in this class and intended to be applied first
        # __registered_transformation are implemented elsewhere
        # __post_transformations are intended to be applied last, after resizing of image!
        self.__transformations = {
            'post': OrderedDict({"info": self.__add_info_to_frame,}),
            'basic': OrderedDict({
                "vflip": lambda img: cv2.flip(img, 1),
                "hflip": lambda img: cv2.flip(img, 0),
                "gray": lambda img: bgr_to_grayscale_bgr(img)}),
            "registered": OrderedDict({
                "smooth": transformer.Smoother(0.6),
                "delta": transformer.Test(1)})
        }
        self.__active_transformations =dict(basic=['vflip', 'hflip'], registered=[], post=[])
        self.__times = deque([], 10)
        self._last_frame = None
        self._last_frame_br = None
        self._last_frame_brp = None

    def get_active_transformations(self, key):
        return list(self.__active_transformations[key])

    def set_active_transformations(self, key, transformations):
        self.__active_transformations[key] = set(transformations)
        print(' - ACTIVE:', key, self.__active_transformations[key])

    def get_keys_of_transformations(self, key):
        return list(self.__transformations[key].keys())

    def get_transformation(self, key_group, key):
        return self.__transformations[key_group][key]

    def release(self):
        """releases camera"""
        self.__adapter.release()

    def single_run_get_frame(self) -> np.array:
        """reads image from camera and optionally applies transformation
            keeps copy of transformed image as self.last_array
        Returns:
            numpy.array: Image taken by camera
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
        image = self.__apply_transformations('basic', image)
        self._last_frame_br = self.__apply_transformations('registered', image)
        self._last_frame_brp = self.__apply_transformations('post', self._last_frame_br)
        self.__times.append(time.time() - starttime)
        return image

    def __apply_transformations(self, key, image):
        try:
            for transformation in self.__transformations[key].keys():
                if transformation in self.__active_transformations[key]:
                    image = self.__transformations[key][transformation](image)
        except Exception as e:
            print(e)
        return image


    def __thread_func(self):
        self.__running = True
        while self.__running:
            self.single_run_get_frame()

    def run(self):
        thread = Thread(target=self.__thread_func, args=())
        thread.start()

    def stop(self):
        self.__running = False

    def running(self):
        return self.__running

    def __make_stream_default_image(self):
        img = np.ones((120, 160, 3))*50
        img = cv2.putText(
            img,
            "Camera not running",
            (10, 60),
            self.__font,
            .4,
            #(0, 0, 0),
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
        return img

    def get_stream_frame_as_bytes(self) -> bytes:
        """returns byte code of an image
            if camera is running the byte-code of a new image is returned
            else the byte-code of the previous image is returned

        Returns:
            bytes: byte-code
        """
        if self.__running and not self._last_frame_br is None:
            frame = cv2.resize(self._last_frame_br, (160, 120), interpolation=cv2.INTER_LINEAR)
            frame = self.__apply_transformations('post', frame)
            _, jpeg = cv2.imencode(".jpg", frame)
            self.__last_transformed_frame_as_bytes = jpeg.tobytes()
        elif not hasattr(self, '__last_transformed_frame_as_bytes'):
            frame = self.__make_stream_default_image()
            _, jpeg = cv2.imencode(".jpg", frame)
            self.__last_transformed_frame_as_bytes = jpeg.tobytes()
        return self.__last_transformed_frame_as_bytes

    def get_last_frame(self) -> np.array:
        """returns stored last image

        Returns:
            np.array: Image
        """
        return self._last_frame

    def get_last_transformed_frame(self):
        if not self.running():
            return self.single_run_get_frame()
        return self._last_frame_brp
    
    def get_and_store_last_transformed_frame(self):
        self.__image = self.get_last_transformed_frame()
        return self.__image

    def __add_info_to_frame(self, frame) -> np.array:
        """adds frame number to image

        Args:
            frame (np.array): Image

        Returns:
            np.array: Image
        """
        time_ms = sum(self.__times) / len(self.__times) * 1000
        return cv2.putText(
            frame,
            f"{round(time_ms,3)} ms",
            (10, 30),
            self.__font,
            .5,
            (0, 0, 0),
            # (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

    def save_stored_image_to_file(self, filepath) -> None:
        """writes image to file

        Args:
            filepath (str): filepath
        """
        cv2.imwrite(filepath, self.__image)

    def check(self) -> bool:
        """check if camera if available

        Returns:
            bool: True means that camera is available
        """
        return self.__adapter.check()

    def get_size(self):
        return self.__adapter.get_size()


def encode_frame_as_jpg(frame):
    _, buffer = cv2.imencode(".jpg", frame)
    dataURI = "data:image/jpeg;base64, " + base64.b64encode(buffer.tobytes()).decode(
        "ascii"
    )
    return dataURI


def gen(camera: CameraController):
    """returns generator generating the byte-code of the single images

    Args:
        camera (Camera): needs to provide method get_frame_as_bytes

    Yields:
        bytes: bytecode of the image for stream
    """
    while True:
        frame = camera.get_stream_frame_as_bytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")


if __name__ == "__main__":
    cam = CameraController()
    res, img = cam.video.read()
    print(res, type(img))
