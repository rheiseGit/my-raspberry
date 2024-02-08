import cv2
import numpy as np


class Parameter:
    def __init__(self, name, value, vmin=None, vmax=None):
        self.name = name
        self.value = value
        self.vmin = vmin
        self.vmax = vmax


class Smoother:
    """Implements exponential smoothing in time-domain"""

    def __init__(self, alpha):
        self.__last_frame = None
        self.parameter = dict(
            alpha=Parameter(name="Alpha", value=alpha, vmin=0, vmax=1)
        )

    def __call__(self, frame):
        alpha = self.parameter["alpha"].value
        if self.__last_frame is None:
            self.__last_frame = frame
        else:
            self.__last_frame = cv2.addWeighted(
                self.__last_frame, alpha, frame, 1 - alpha, 0.0
            )

        return self.__last_frame

    def reset(self):
        self.__last_frame = None


class SimpleMotionDetection:
    def __init__(
        self, alpha=0.9, beta=0.4, threshold=20, blur=20, gbks=3, action_threshold=6
    ):
        self.__frame1 = None
        self.__frame2 = None
        self.parameter = dict(
            gbks=Parameter(name="GBKS", value=gbks, vmin=0, vmax=50),
            alpha=Parameter(name="Alpha", value=alpha, vmin=0, vmax=1),
            beta=Parameter(name="Beta", value=beta, vmin=0, vmax=1),
            threshold=Parameter(name="Threshold", value=threshold, vmin=0, vmax=255),
            maskblur=Parameter(name="Blur", value=blur, vmin=0, vmax=100),
            action_threshold=Parameter(
                name="AT", value=action_threshold, vmin=1, vmax=100
            ),
        )
        self.__last_image_detected = None

    def __call__(self, frame):
        bwframe = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        gbks = self.parameter["gbks"].value
        bwframe = cv2.GaussianBlur(bwframe, (gbks, gbks), 0)
        alpha = self.parameter["alpha"].value
        beta = self.parameter["beta"].value
        threshold = self.parameter["threshold"].value
        blur = self.parameter["maskblur"].value
        action_threshold = self.parameter["action_threshold"].value
        if self.__last_image_detected is None:
            self.__last_image_detected = np.ones(frame.shape) * 100
        if self.__frame1 is None or self.__frame2 is None:
            self.__frame1 = bwframe
            self.__frame2 = bwframe
            self.__diff_frame = cv2.absdiff(self.__frame2, self.__frame1)
        else:
            self.__frame1 = cv2.addWeighted(
                self.__frame1, alpha, bwframe, 1 - alpha, 0.0
            )
            self.__frame2 = cv2.addWeighted(self.__frame2, beta, bwframe, 1 - beta, 0.0)

            # Difference of frames
        diff_frame = cv2.absdiff(self.__frame2, self.__frame1)
        self.__diff_frame = cv2.addWeighted(
            self.__diff_frame, alpha, diff_frame, 1 - alpha, 0.0
        )

        # Threshold for differences
        diff_frame = cv2.absdiff(self.__diff_frame, diff_frame)
        value = np.mean(diff_frame)
        # print(value)
        _, mask = cv2.threshold(diff_frame, threshold, 255, cv2.THRESH_BINARY)

        # Blurring of differences
        mask2 = cv2.blur(mask, (blur, blur))
        _, mask2 = cv2.threshold(mask2, 1, 255, cv2.THRESH_BINARY)

        # d4 = cv2.GaussianBlur(d4, (blur, blur), 10)
        # d4 = cv2.dilate(d4, None, iterations=4)

        # d5 = cv2.cvtColor(d4, cv2.COLOR_GRAY2BGR)
        bwframe_bgr = cv2.cvtColor(bwframe, cv2.COLOR_GRAY2BGR)
        frame_masked = cv2.bitwise_and(frame, frame, mask=mask2)
        frame_masked2 = cv2.bitwise_and(
            bwframe_bgr, bwframe_bgr, mask=cv2.bitwise_not(mask2)
        )

        d1 = cv2.cvtColor(self.__frame1, cv2.COLOR_GRAY2BGR)
        d2 = cv2.cvtColor(self.__frame2, cv2.COLOR_GRAY2BGR)
        d3 = cv2.cvtColor(
            (self.__diff_frame / max(100, np.max(self.__diff_frame)) * 255).astype(
                "uint8"
            ),
            cv2.COLOR_GRAY2BGR,
        )

        d4 = cv2.cvtColor(diff_frame, cv2.COLOR_GRAY2BGR)
        d5 = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        d6 = cv2.cvtColor(mask2, cv2.COLOR_GRAY2BGR)
        d7 = cv2.addWeighted(frame_masked, 1, frame_masked2, 0.5, 0.0)

        # d8 = frame
        if value > action_threshold:
            d8 = frame
            self.__last_image_detected = frame
        else:
            d8 = bwframe_bgr
        d9 = self.__last_image_detected

        # d4 = cv2.cvtColor(d4, cv2.COLOR_GRAY2BGR)
        # img = cv2.bitwise_and(frame, frame, mask=d3)
        img1 = np.hstack((d1, d2, d3))
        img2 = np.hstack((d4, d5, d6))
        img3 = np.hstack((d7, d8, d9))
        img = np.vstack((img1, img2, img3))

        return img

    def reset(self):
        self.__frame1 = None
        self.__frame2 = None


class Test:
    """Implements exponential smoothing in time-domain"""

    def __init__(self, beta):
        self.__last_frame = None
        self.parameter = dict(beta=Parameter(name="Beta", value=beta, vmin=0, vmax=1))

    def __call__(self, frame):
        beta = self.parameter["beta"].value
        if self.__last_frame is None:
            self.__last_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            return frame
        else:
            bwframe = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            h, w = bwframe.shape
            h1 = int(0.2 * h)
            h2 = int(0.8 * h)
            mask = np.zeros(bwframe.shape).astype("int8")
            mask[h1:h2] = 255
            mask_inv = cv2.bitwise_not(mask)
            img = cv2.bitwise_and(frame, frame, mask=mask)
            return img

    def reset(self):
        self.__last_frame = None
