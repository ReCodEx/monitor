#!/usr/bin/env python3

import unittest
import asyncio
from unittest.mock import *
from monitor.websocket_connections import WebsocketServer


class TestWebsocketServer(unittest.TestCase):
    @patch('asyncio.set_event_loop')
    @patch('websockets.serve')
    def test_init(self, mock_websock_serve, mock_set_loop):
        loop = MagicMock()
        logger = MagicMock()
        mock_websock_serve.return_value = "0101"
        WebsocketServer.connection_handler = MagicMock()
        server = WebsocketServer(("ip_address", 4512), None, loop, logger)

        self.assertEqual(server._loop, loop)
        self.assertIsNone(server._connections)
        mock_set_loop.assert_called_once_with(loop)
        mock_websock_serve.assert_called_once_with(server.connection_handler, "ip_address", 4512)
        loop.run_until_complete.assert_called_once_with("0101")

    def test_connection_handler(self):
        queue = asyncio.Queue()
        logger = MagicMock()
        connection_mock = MagicMock()
        connection_mock.add_client.return_value = queue
        connection_mock.remove_client.return_value = None

        websocket_mock = MagicMock()

        received_id = asyncio.Future()
        received_id.set_result("1234")
        websocket_mock.recv.return_value = received_id
        websocket_mock.send.return_value = [None]

        loop = asyncio.new_event_loop()
        queue.put_nowait("result text")
        queue.put_nowait(None)

        websock_server = WebsocketServer(("localhost", 11111), connection_mock, loop, logger)
        # actually call the method
        loop.run_until_complete(websock_server.connection_handler(websocket_mock, None))

        # test the constraints
        websocket_mock.recv.assert_called_once_with()
        websocket_mock.send.assert_called_once_with('result text')
        connection_mock.add_client.assert_called_once_with("1234")
        connection_mock.remove_client.assert_called_once_with("1234")

    @patch('asyncio.set_event_loop')
    def test_run(self, mock_set_loop):
        loop = MagicMock()
        logger = MagicMock()
        server = WebsocketServer(("ip_address", 123), None, loop, logger)
        server.run()
        mock_set_loop.assert_called_with(loop)
        loop.run_forever.assert_called_once_with()
