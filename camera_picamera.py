from time import sleep

import picamera
import picamera.array
import numpy as np

from camera_base import Camera
from shared import get_image_publisher


class CameraPicamera(Camera):

    def __init__(self, cap_fps: int = 10, resolution=(2592, 1944), run=True, **kwargs) -> None:
        super().__init__(**kwargs)
        self.fps = cap_fps
        self.res = resolution
        self.buffer = None
        self.camera = picamera.PiCamera()
        self.configure(self.camera, self.res, self.fps)
        self.output = picamera.array.PiRGBArray(self.camera)

        if run:
            self.start()

    @staticmethod
    def configure(camera, res, fps):
        camera.resolution = res
        camera.framerate = fps

        camera.sharpness = 0
        camera.contrast = 0
        camera.brightness = 50
        camera.saturation = 0
        camera.ISO = 0
        camera.video_stabilization = False
        camera.exposure_compensation = 0
        camera.exposure_mode = 'auto'
        camera.meter_mode = 'average'
        camera.awb_mode = 'auto'
        camera.image_effect = 'none'
        camera.color_effects = None
        camera.rotation = 0
        camera.hflip = True
        camera.vflip = True
        camera.crop = (0.0, 0.0, 1.0, 1.0)

        for i in range(10):
            if camera.analog_gain > 1:
                break
            sleep(0.1)

        # Now fix the values
        camera.shutter_speed = camera.exposure_speed  # 10**6//90#
        camera.exposure_mode = 'off'
        g = camera.awb_gains
        camera.awb_mode = 'off'
        camera.awb_gains = g

    def step(self):
        self.camera.capture(self.output, 'rgb')
        if self.buffer is None:
            self.buffer = get_image_publisher("shm://camera", self.output.array.shape, np.uint8)
            print(self.output.array.shape)
        self.buffer[:] = self.output.array
        self.output.truncate(0)


if __name__ == '__main__':
    camera_worker = CameraPicamera()
