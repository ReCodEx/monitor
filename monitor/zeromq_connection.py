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
    def __init__(self, address, port, logger):
        """
        Initialize new instance with given address and port.
        :param address: String representation of IP address
        to listen to or a hostname.
        :param port: String port where to listen.
        :param logger: System logger
        """
        self._logger = logger
        context = zmq.Context()
        self._receiver = context.socket(zmq.PULL)
        address = "tcp://{}:{}".format(address, port)
        self._receiver.bind(address)
        self._logger.info("zeromq server initialized at {}".format(address))

    def start(self, message_callback):
        """
        Start receiving messages from underlying zeromq socket.
        :param message_callback: Function to be called when new messages arrived.
        This function should not block for long. Required are two parameters, first
        is id of stream and second is text of the message. Both are strings.
        :return: True if exited normally (by "exit" message with ID 0), False if
        socket error occurred.
        """
        while True:
            # try to receive a message
            try:
                message = self._receiver.recv_string()
                self._logger.debug("zeromq server: got message '{}'".format(message))
            except Exception as e:
                self._logger.error("zeromq server: socket error: {}".format(e))
                return False
            # split given message
            try:
                client_id, data = message.split(',')
            except ValueError:
                continue
            if client_id == "0" and data == "exit":
                self._logger.info("zeromq server: got shutdown command")
                break
            # call registered callback with given data
            message_callback(client_id, data)
        return True
