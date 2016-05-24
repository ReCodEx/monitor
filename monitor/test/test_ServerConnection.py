#!/usr/bin/env python3

import unittest
import zmq
from unittest.mock import *
from monitor.zeromq_connection import ServerConnection


class TestServerConnection(unittest.TestCase):
    @patch('zmq.Context')
    def test_init(self, mock_context):
        mock_socket = MagicMock()
        mock_receiver = MagicMock()
        logger = MagicMock()
        mock_context.return_value = mock_socket
        mock_socket.socket.return_value = mock_receiver

        ServerConnection("ip_address", 1025, logger)
        mock_context.assert_called_once_with()
        mock_socket.socket.assert_called_once_with(zmq.ROUTER)
        mock_receiver.setsockopt.assert_called_once_with(zmq.IDENTITY, b"recodex-monitor")
        mock_receiver.bind.assert_called_once_with("tcp://ip_address:1025")

    @patch('zmq.Context')
    def test_start_normal(self, mock_context):
        mock_socket = MagicMock()
        mock_receiver = MagicMock()
        logger = MagicMock()
        mock_context.return_value = mock_socket
        mock_socket.socket.return_value = mock_receiver
        mock_callback = MagicMock()

        server = ServerConnection("ip_address", 1025, logger)
        mock_receiver.recv_multipart.side_effect = [[b"id", b"1234", b"command text", b"task id text",
                                                     b"task state text"], [b"id", b"0", b"exit"]]
        ret = server.start(mock_callback)

        self.assertTrue(ret)
        mock_callback.assert_called_once_with("1234", '{"command": "command text", "task_id": "task id text", '
                                              '"task_state": "task state text"}')

    @patch('zmq.Context')
    def test_start_socket_error(self, mock_context):
        mock_socket = MagicMock()
        mock_receiver = MagicMock()
        logger = MagicMock()
        mock_context.return_value = mock_socket
        mock_socket.socket.return_value = mock_receiver
        mock_callback = MagicMock()

        server = ServerConnection("ip_address", 1025, logger)
        mock_receiver.recv_multipart.side_effect = Exception
        ret = server.start(mock_callback)

        self.assertFalse(ret)
        self.assertFalse(mock_callback.called)
