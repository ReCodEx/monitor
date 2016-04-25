#!/usr/bin/env python3
"""
Testing tool for sending messages to zeromq connection with monitor.
"""

import zmq


context = zmq.Context()
zmq_socket = context.socket(zmq.PUSH)
zmq_socket.connect("tcp://127.0.0.1:7894")

print("Write messages with format <ID>,<MESSAGE>")
try:
    while True:
        message = input("> ")
        zmq_socket.send_string(message)
        if message == "0,exit":
            break
except KeyboardInterrupt:
    pass
finally:
    print("Quitting...")
