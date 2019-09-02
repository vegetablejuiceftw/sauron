from threading import Thread
from typing import Iterable, Callable, Dict, List

from pydantic import BaseModel
from zeroless import (Server, Client)


class Ports:
    detection = 12000,
    servo = 12010, 12020


class Topics:
    detection = "position"
    servo = "servo"


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


class Detection(BaseModel):
    points: List[DetectionPosition]


def get_listener(ports: list, topics: list) -> Iterable:
    # Connects the client to as many servers as desired
    client = Client()
    for port in ports:
        client.connect_local(port=port)

    # Assigns an iterable to wait for incoming messages with the topics
    listen_for_pub = client.sub(topics=[t.encode('utf-8') for t in topics])
    return listen_for_pub


class CallbackListener(Thread):

    def __init__(self, generator, callback=None, daemon=True, **kwargs) -> None:
        Thread.__init__(self, daemon=daemon, **kwargs)
        self.generator = generator
        self.callback = callback
        self.start()
        self.messages = {}

    def run(self) -> None:
        for values in self.generator:
            if len(values) == 2:
                topic, msg = values
                topic = topic.decode()
                self.messages[topic] = msg
                self.callback and self.callback(topic, msg)
            else:
                print("whut the heck", values)


def get_server(port: int, topics: List[str]) -> Dict[str, Callable]:
    # And assigns a callable to publish messages with the topics'
    srv = Server(port=port)

    mapping = {topic: srv.pub(topic=topic.encode('utf-8'), embed_topic=True) for topic in topics}
    return {k: (lambda packet: v(packet.json().encode('utf-8'))) for k, v in mapping.items()}