#!/usr/bin/env python3
"""
Handle zeromq socket.
"""

import zmq


class ServerConnection:
    def __init__(self, address, port):
        context = zmq.Context()
        # receive work
        self._receiver = context.socket(zmq.PULL)
        self._receiver.bind("tcp://{}:{}".format(address, port))

    def start(self, message_callback):
        while True:
            message = self._receiver.recv_string()
            try:
                client_id, data = message.split(',')
                if data == "exit":
                    break
                message_callback(client_id, data)
            except:
                continue
