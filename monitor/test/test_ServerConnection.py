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
        mock_context.return_value = mock_socket
        mock_socket.socket.return_value = mock_receiver

        ServerConnection("ip_address", 1025)
        mock_context.assert_called_once_with()
        mock_socket.socket.assert_called_once_with(zmq.PULL)
        mock_receiver.bind.assert_called_once_with("tcp://ip_address:1025")

    @patch('zmq.Context')
    def test_start_normal(self, mock_context):
        mock_socket = MagicMock()
        mock_receiver = MagicMock()
        mock_context.return_value = mock_socket
        mock_socket.socket.return_value = mock_receiver
        mock_callback = MagicMock()

        server = ServerConnection("ip_address", 1025)
        mock_receiver.recv_string.side_effect = ["1234,message text", "0,exit"]
        ret = server.start(mock_callback)

        self.assertTrue(ret)
        mock_callback.assert_called_once_with("1234", "message text")

    @patch('zmq.Context')
    def test_start_socket_error(self, mock_context):
        mock_socket = MagicMock()
        mock_receiver = MagicMock()
        mock_context.return_value = mock_socket
        mock_socket.socket.return_value = mock_receiver
        mock_callback = MagicMock()

        server = ServerConnection("ip_address", 1025)
        mock_receiver.recv_string.side_effect = Exception
        ret = server.start(mock_callback)

        self.assertFalse(ret)
        self.assertFalse(mock_callback.called)
