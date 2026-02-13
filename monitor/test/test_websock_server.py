#!/usr/bin/env python3

import unittest
import asyncio
from unittest.mock import ANY, AsyncMock, MagicMock, patch
from monitor.websocket_connections import WebsocketServer


class TestWebsocketServer(unittest.TestCase):
    @patch('monitor.websocket_connections.serve')
    def test_init(self, mock_websock_serve):
        loop = asyncio.new_event_loop()
        logger = MagicMock()
        server = WebsocketServer(("ip_address", 4512), None, loop, logger)

        self.assertEqual(server._loop, loop)
        self.assertIsNone(server._connections)
        mock_websock_serve.assert_not_called()
        loop.close()

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
    @patch('monitor.websocket_connections.serve', new_callable=AsyncMock)
    def test_run(self, mock_websock_serve, mock_set_loop):
        loop = asyncio.new_event_loop()
        logger = MagicMock()

        server_obj = MagicMock()
        wait_closed_future = loop.create_future()
        wait_closed_future.set_result(None)
        server_obj.wait_closed.return_value = wait_closed_future
        mock_websock_serve.return_value = server_obj

        server = WebsocketServer(("ip_address", 123), None, loop, logger)

        loop.call_later(0.05, loop.stop)
        server.run()

        mock_set_loop.assert_called_with(loop)
        mock_websock_serve.assert_awaited_once_with(ANY, "ip_address", 123)
        server_obj.close.assert_called_once_with()
        loop.close()
