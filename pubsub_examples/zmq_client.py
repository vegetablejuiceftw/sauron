from time import time

import zmq

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

#  Do 10 requests, waiting each time for a response
while True:
    socket.send(b"%f" % time())

    #  Get the reply.
    message = socket.recv()
    print("Received reply %s %.6f" % (message, time() - float(message)))