import cv2 as cv
import numpy as np

from camera_base import Camera
from shared import get_image_publisher


class CameraOpenCV(Camera):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.grabber = cv.VideoCapture(self.kwargs.get('index', 0))
        frame = self.grabber.read()[1]
        half = cv.resize(frame, (0, 0), fx=0.5, fy=0.5)
        self.shape = frame.shape
        self.shape_half = half.shape

        self.raw = get_image_publisher("shm://camera", self.shape, np.uint8)
        self.raw_half = get_image_publisher("shm://camera-half", self.shape_half, np.uint8)

    def step(self):
        self.grabber.read(self.raw)
        self.raw_half[:] = cv.resize(self.raw, (0, 0), fx=0.5, fy=0.5)


if __name__ == '__main__':
    camera_worker = CameraOpenCV()
    camera_worker.start()
