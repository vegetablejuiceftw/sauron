from time import time

import snakemq.link
import snakemq.packeter
import snakemq.messaging
import snakemq.message

my_link = snakemq.link.Link()
my_packeter = snakemq.packeter.Packeter(my_link)
my_messaging = snakemq.messaging.Messaging("AAA", "", my_packeter)

my_link.add_connector(("localhost", 4000))
my_link.add_connector(("localhost", 4001))


def on_recv(conn, ident, message):
    print(ident, message.data, time())


my_messaging.on_message_recv.add(on_recv)

my_link.loop()
