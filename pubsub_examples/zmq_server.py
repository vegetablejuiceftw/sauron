from time import time

import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    #  Wait for next request from client
    message = socket.recv()
    socket.send(message)

    print("Received request:  %s %.6f" % (message, time() - float(message)))

