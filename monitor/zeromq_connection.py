#!/usr/bin/env python3
"""
Handle zeromq socket.
"""

import zmq
import json


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
        self._receiver = context.socket(zmq.ROUTER)
        self._receiver.setsockopt(zmq.IDENTITY, b"recodex-monitor")
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
                message = self._receiver.recv_multipart()
                self._logger.debug("zeromq server: got message '{}'".format(message))
            except Exception as e:
                self._logger.error("zeromq server: socket error: {}".format(e))
                return False
            # split given message
            try:
                """
                decode the message with following parts:
                    0 - zeromq identity of sender
                    1 - byte array with channel id
                    2 - byte array with message command
                    3 - byte array with message task_id - only for TASK command
                    4 - byte array with message task_state - only for TASK command
                """
                decoded_message = [item.decode() for item in message[1:]]
                client_id = decoded_message[0]
                keys = ["command", "task_id", "task_state"]
                data = json.dumps(dict(zip(keys, decoded_message[1:])), sort_keys=True)
            except ValueError:
                continue
            if client_id == "0" and data == '{"command": "exit"}':
                self._logger.info("zeromq server: got shutdown command")
                break
            # call registered callback with given data
            message_callback(client_id, data)

            # after last message (command FINISHED) send also poison pill
            # to close listening sockets
            if decoded_message[1] == "FINISHED":
                message_callback(client_id, None)
        return True
