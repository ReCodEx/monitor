#!/usr/bin/env python3
"""
Handle zeromq socket.
"""

import zmq


class ServerConnection:
    """
    Class responsible for creating zeromq socket (server) and receiving
    messages from connected clients. The message should be text with
    format <ID>,<MESSAGE>, where text <MESSAGE> will be sent to websocket
    client subscribed to channel <ID>.
    """
    def __init__(self, address, port):
        """
        Initialize new instance with given address and port.
        :param address: String representation of IP address
        to listen to or a hostname.
        :param port: String port where to listen.
        """
        context = zmq.Context()
        self._receiver = context.socket(zmq.PULL)
        self._receiver.bind("tcp://{}:{}".format(address, port))

    def start(self, message_callback):
        """
        Start receiving messages from underlying zeromq socket.
        :param message_callback: Function to be called when new messages arrived.
        This function should not block for long. Required are two parameters, first
        is id of stream and second is text of the message. Both are strings.
        :return: Nothing
        """
        while True:
            # try to receive a message
            try:
                message = self._receiver.recv_string()
            except Exception as e:
                print("ZMQ socket error: {}".format(e))
                break
            # split given message
            try:
                client_id, data = message.split(',')
            except ValueError:
                continue
            if data == "exit":
                break
            # call registered callback with given data
            message_callback(client_id, data)
