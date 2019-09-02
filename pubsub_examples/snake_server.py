from time import time, sleep

import snakemq.link
import snakemq.packeter
import snakemq.messaging
import snakemq.message

my_link = snakemq.link.Link()
my_packeter = snakemq.packeter.Packeter(my_link)
my_messaging = snakemq.messaging.Messaging('BBB', "", my_packeter)

my_link.add_listener(("", 4000))  # listen on all interfaces and on port 4000
my_link.add_connector(("localhost", 4001))

message = snakemq.message.Message(b"hello %f" % time(), ttl=600)
my_messaging.send_message("AAA", message)

my_link.loop()
