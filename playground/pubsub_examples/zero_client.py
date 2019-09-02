from time import time

from zeroless import (Server, Client)

# Connects the client to as many servers as desired
client = Client()
client.connect_local(port=12345)

# Initiate a subscriber client
# Assigns an iterable to wait for incoming messages with the topic 'sh'
listen_for_pub = client.sub(topics=[b'topic_name'])

for topic, msg in listen_for_pub:
    print(topic, ' - %.6f' % (time() - float(msg)))