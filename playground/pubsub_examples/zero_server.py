from time import sleep, time

from zeroless import (Server, Client)

# Binds the publisher server to port 12345
# And assigns a callable to publish messages with the topic 'sh'
pub = Server(port=12345).pub(topic=b'topic_name', embed_topic=True)

# Gives publisher some time to get initial subscriptions
while True:
    pub(b"%f" % time())
    sleep(0.2)
