import cv2
import numpy as np
import time
import picamera2

CAMERA_INDEX = -1
print("Camera-Index", CAMERA_INDEX)


class AdapterOpenCV:
    def __init__(self):
        self.vc = cv2.VideoCapture(-1)

    def read(self) -> np.array:
        success, image = self.vc.read()
        return image

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
    def __init__(self):
        self.pc = picamera2.Picamera2()
        # self.video_config = self.pc.create_video_configuration(
        #    main={"size": (160, 120)}, lores={"size": (160, 120)}, display="lores"
        # )
        # self.pc.configure(self.video_config)
        self.pc.start()

    def read(self) -> np.array:
        image = self.pc.capture_array("main")
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return image

    def release(self):
        self.pc.stop()
        self.pc.close()
        print("--")

    def check(self):
        return True


class CameraController(object):
    def __init__(self, adapter):
        self.adapter = adapter
        self.use_grayscale = False
        self.flip_v = False
        self.flip_h = False
        self.info = False
        self.counter = 0
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.running = True

    def release(self):
        """releases camera"""
        self.video.release()

    def get_next_frame(self) -> np.array:
        """reads image from camera and optionally applies transformation
            keeps copy of transformed image as self.last_array
        Returns:
            numpy.array: Image taken by camera
        """
        self.counter += 1
        # print(self.check())
        # time.sleep(1)
        try:
            image = self.adapter.read()
            # print(type(image))
        except Exception as e:
            print(self.counter, e)
            image = np.ones((10, 10, 3))
        try:
            if self.flip_v:
                image = cv2.flip(image, 1)
            if self.flip_h:
                image = cv2.flip(image, 0)
            if self.use_grayscale:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            if self.info:
                image = self.add_info(image)
        except Exception as e:
            print(e)
        if image is None:
            image = np.ones((10, 10, 3))
        self.last_frame = image.copy()
        return image

    def get_frame_as_bytes(self) -> bytes:
        """returns byte code of an image
            if camera is running the byte-code of a new image ist returned
            else the byte-code of the last image taken

        Returns:
            bytes: byte-code
        """
        if self.running:
            frame = self.get_next_frame()
            ret, jpeg = cv2.imencode(".jpg", frame)
            self.last_frame_as_bytes = jpeg.tobytes()
        else:
            pass
        return self.last_frame_as_bytes

    def get_last_frame(self) -> np.array:
        """returns stored last image

        Returns:
            np.array: Iamge
        """
        return self.last_frame

    def add_info(self, frame) -> np.array:
        """adds frame number to image

        Args:
            frame (np.array): Image

        Returns:
            np.array: Image
        """
        return cv2.putText(
            frame,
            f"{self.counter}",
            (10, 40),
            self.font,
            1,
            (0, 255, 255),
            1,
            cv2.LINE_AA,
        )

    def save_last_frame_to_file(self, filepath) -> None:
        """writes image to file

        Args:
            filepath (str): filepath
        """
        cv2.imwrite(filepath, self.last_frame)

    def check(self) -> bool:
        """check if camera if available

        Returns:
            bool: True means that camera is available
        """
        return self.adapter.check()


def gen(camera: CameraController):
    """returns generator generating the byte-code of the single images

    Args:
        camera (Camera): needs to provide method get_frame_as_bytes

    Yields:
        bytes: bytecode of the image for stream
    """
    while True:
        frame = camera.get_frame_as_bytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")


if __name__ == "__main__":
    cam = CameraController()
    res, img = cam.video.read()
    print(res, type(img))
