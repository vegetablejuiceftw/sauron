from threading import Thread
from typing import Optional


class Camera(Thread):
    def __init__(self, zoom: float = 1.0, quality: int = 80, **kwargs) -> None:
        Thread.__init__(self, **kwargs)
        self.kwargs = kwargs
        self.zoom = zoom
        self.quality = quality
        self.grabber = None
        self.raw = None
        self.image: Optional[str] = None
        self.detection: dict = {}

    def get_grabber(self):
        return self.grabber

    def step(self):
        raise NotImplemented

    def get_jpg(self) -> str:
        return self.image

    def get_detection(self) -> dict:
        return self.detection

    def run(self):
        while True:
            self.step()
