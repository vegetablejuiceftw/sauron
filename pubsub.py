from threading import Thread
from typing import Iterable, Callable, Dict, List, NamedTuple, Generator

from zeroless import Server, Client

from messages import DetectionPacket, Delta, BaseMessageType


class TopicNames:
    detection = "detection"
    servo = "servo"


class Services:
    detector = 12000
    web_server = 12010
    autonomous = 12020


class Channel(NamedTuple):
    topic_name: str
    ports: List[int]
    packet: BaseMessageType


class Topics:
    channels = [
        Channel("detection", [Services.detector], DetectionPacket),
        Channel("servo", [Services.web_server, Services.autonomous], Delta),
    ]

    mapping = {c.topic_name: c for c in channels}

    services = set(service for c in channels for service in c.ports)

    @classmethod
    def get_service_topics(cls, service_port: int):
        return [c.topic_name for c in cls.channels if service_port in c.ports]

    @classmethod
    def start_service(cls, service_port: int):
        return get_server(port=service_port, topics=cls.get_service_topics(service_port))

    @classmethod
    def start_listener(cls, *topics: str):
        channels = [channel for channel in cls.channels if channel.topic_name in topics]
        return get_listener(*channels)


def get_mapped_stream(client, *channels: Channel) -> Generator[BaseMessageType, None, None]:
    topic_mapping: Dict[str, BaseMessageType] = {channel.topic_name: channel.packet for channel in channels}

    stream: Iterable = client.sub(topics=[t.encode('utf-8') for t in topic_mapping.keys()])

    for values in stream:
        # malformed message
        if len(values) != 2:
            print("malformed package", values)
            continue

        topic, raw_msg = values

        topic_name: str = topic.decode()
        message = topic_mapping.get(topic_name)
        if message:
            try:
                yield topic_name, message.parse_raw(raw_msg)
            except Exception as e:
                print(f"Failed topic {topic_name} -> {message}, '{raw_msg}'", e)


def get_listener(*channels: Channel):
    # Connects the client to as many servers as desired
    client = Client()

    # connect to all ports
    ports = sum([channel.ports for channel in channels], [])
    for port in ports:
        client.connect_local(port=port)

    # Assigns an iterable to wait for incoming messages with the topics
    return get_mapped_stream(client, *channels)


class CallbackListener(Thread):

    def __init__(self, generator, callback=None, daemon=True, run=True, **kwargs) -> None:
        Thread.__init__(self, daemon=daemon, **kwargs)
        self.generator = generator
        self.callback = callback
        self.messages: Dict[str, BaseMessageType] = {}

        if run:
            self.start()

    def run(self) -> None:
        for values in self.generator:
            topic, msg = values
            self.messages[topic] = msg
            self.callback and self.callback(topic, msg)


def get_server(port: int, topics: List[str]) -> Dict[str, Callable[[BaseMessageType], None]]:
    # And assigns a callable to publish messages with the topics'
    srv = Server(port=port)

    mapping = {topic: srv.pub(topic=topic.encode('utf-8'), embed_topic=True) for topic in topics}
    return {k: (lambda packet: v(packet.json().encode('utf-8'))) for k, v in mapping.items()}
