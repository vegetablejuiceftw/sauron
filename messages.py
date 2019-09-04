from typing import List, Type

from pydantic import BaseModel

BaseMessageType = Type[BaseModel]


class Delta(BaseModel):
    dx: float
    dy: float
    time: float = None


class DetectionPosition(BaseModel):
    x: int
    y: int
    w: int
    h: int
    sx: int
    sy: int
    id: int
    pid: int
    age: int
    color: tuple
    ms: float

    @property
    def cx(self):
        return int(self.x + self.w / 2)

    @property
    def cy(self):
        return int(self.y + self.h / 2)

    @property
    def dx(self):
        return 0.5 - self.cx / self.sx

    @property
    def dy(self):
        return 0.5 - self.cy / self.sy

    @property
    def key(self):
        return abs(self.dx) + abs(self.dy)

    def zoom(self, zoom):
        return DetectionPosition(
            x=int(self.x / zoom),
            y=int(self.y / zoom),
            w=int(self.w / zoom),
            h=int(self.h / zoom),
            sx=int(self.sx / zoom),
            sy=int(self.sy / zoom),
            id=self.id,
            pid=self.pid,
            age=self.age,
            color=self.color,
            ms=self.ms,
        )


class DetectionPacket(BaseModel):
    points: List[DetectionPosition]
