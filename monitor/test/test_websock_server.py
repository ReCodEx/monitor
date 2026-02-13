#!/usr/bin/env python3

import unittest
import asyncio
from unittest.mock import *
from monitor.websocket_connections import WebsocketServer


class TestWebsocketServer(unittest.TestCase):
    @patch('asyncio.set_event_loop')
    @patch('monitor.websocket_connections.serve')
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

    @patch('monitor.websocket_connections.serve')
    def test_connection_handler(self, mock_websock_serve):
        queue = asyncio.Queue()
        logger = MagicMock()
        connection_mock = MagicMock()
        connection_mock.add_client.return_value = queue
        connection_mock.remove_client.return_value = None

        websocket_mock = MagicMock()

        loop = asyncio.new_event_loop()
        received_id = loop.create_future()
        received_id.set_result("1234")
        response = loop.create_future()
        response.set_result(None)
        websocket_mock.recv.return_value = received_id
        websocket_mock.send.return_value = response
        queue.put_nowait("result text")
        queue.put_nowait(None)

        start_server_future = loop.create_future()
        start_server_future.set_result("0101")
        mock_websock_serve.return_value = start_server_future
        websock_server = WebsocketServer(("localhost", 11111), connection_mock, loop, logger)
        # actually call the method
        loop.run_until_complete(websock_server.connection_handler(websocket_mock))

        # test the constraints
        websocket_mock.recv.assert_called_once_with()
        websocket_mock.send.assert_called_once_with('result text')
        connection_mock.add_client.assert_called_once_with("1234")
        connection_mock.remove_client.assert_called_once_with("1234", queue)

    @patch('asyncio.set_event_loop')
    @patch('monitor.websocket_connections.serve')
    def test_run(self, mock_websock_serve, mock_set_loop):
        loop = MagicMock()
        logger = MagicMock()
        mock_websock_serve.return_value = "0101"
        server = WebsocketServer(("ip_address", 123), None, loop, logger)
        server.run()
        mock_set_loop.assert_called_with(loop)
        loop.run_forever.assert_called_once_with()
