import cv2
import numpy as np

class Parameter():
    def __init__(self, name, value, vmin=None, vmax=None):
        self.name = name
        self.value = value
        self.vmin = vmin
        self.vmax = vmax

class Smoother:
    """Implements exponential smoothing in time-domain"""

    def __init__(self, alpha):
        self.__last_frame = None
        self.parameter = dict(alpha=Parameter(name='Alpha', value=alpha, vmin=0, vmax=1))

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

class Test:
    """Implements exponential smoothing in time-domain"""

    def __init__(self, beta):
        self.__last_frame = None
        self.parameter = dict(beta=Parameter(name='Beta', value=beta, vmin=0, vmax=1))

    def __call__(self, frame):
        beta = self.parameter["beta"].value
        if self.__last_frame is None:
            self.__last_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            return frame
        else:
            bwframe = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            h,w=bwframe.shape
            h1=int(.2*h)
            h2=int(.8*h)
            mask = np.zeros(bwframe.shape).astype('int8')
            mask[h1:h2]=255
            mask_inv=cv2.bitwise_not(mask)
            img = cv2.bitwise_and(frame, frame, mask=mask)
            return img

    def reset(self):
        self.__last_frame = None
