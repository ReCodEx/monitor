#!/usr/bin/env python3
"""
Testing tool for sending messages to zeromq connection with monitor.
"""

import zmq


context = zmq.Context()
zmq_socket = context.socket(zmq.ROUTER)
zmq_socket.connect("tcp://127.0.0.1:7894")

print("Write messages with format <ID>,<MESSAGE>")
try:
    while True:
        message = input("> ")
        id, msg = message.split(',')
        """
        Message has following format:
            - identity of monitor socket
            - id of target channel as byte array
            - text of the message as byte array
        """
        zmq_socket.send_multipart([b"recodex-monitor", id.encode(), msg.encode()])
        if message == "0,exit":
            break
except KeyboardInterrupt:
    pass
finally:
    print("Quitting...")
