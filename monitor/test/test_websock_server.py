#!/usr/bin/env python

import unittest
import asyncio
from unittest.mock import *
from monitor import websocket_connections as wc


class TestWebsocketServer(unittest.TestCase):
    def test_handler(self):
        first_future = asyncio.Future()
        second_future = asyncio.Future()
        connection_mock = MagicMock()
        connection_mock.add_client.return_value = first_future
        connection_mock.update_future.return_value = second_future
        connection_mock.remove_client.return_value = None

        websocket_mock = MagicMock()
        websocket_mock.recv.return_value = MagicMock(return_value="1234")
        websocket_mock.send.return_value = [None]

        loop = asyncio.new_event_loop()
        first_future.set_result("result text")
        second_future.cancel()

        websock_server = wc.WebsocketServer(("localhost", 11111), connection_mock, loop)
        # actually call the method
        loop.run_until_complete(websock_server.connection_handler(websocket_mock, None))

        # test the constraints
        websocket_mock.recv.assert_called_once_with()
        connection_mock.add_client.assert_called_once_with("1234")
