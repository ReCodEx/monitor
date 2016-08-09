#!/usr/bin/env python3

import unittest
import asyncio
from unittest.mock import MagicMock
from monitor.websocket_connections import ClientConnections


class TestClientConnections(unittest.TestCase):
    def setUp(self):
        logger = MagicMock()
        loop = MagicMock
        self._connections = ClientConnections(logger, loop)

    def test_add_client(self):
        queue = self._connections.add_client("1234")
        self.assertNotEqual(queue, None, "No queue returned")
        self.assertIsInstance(queue, asyncio.Queue, "Wrong type of returned value")
        self.assertEqual(queue, self._connections._clients["1234"][0],
                         "Queue not present at requested id")
        queue2 = self._connections.add_client("456777")
        self.assertNotEqual(queue, queue2, "Different clients have same future")
        self._connections.add_client("1234")
        self.assertEqual(len(self._connections._clients["1234"]), 2, "No concurrent clients for same id")

    def test_remove_channel(self):
        self._connections.add_client("1234")
        self._connections.remove_channel("4567")
        self.assertEqual(len(self._connections._clients), 1, "Nonexisting channel removed")
        self._connections.remove_channel("1234")
        self.assertEqual(len(self._connections._clients), 0, "Existing channel not removed")

    def test_remove_client(self):
        queue1 = self._connections.add_client("1234")
        queue2 = self._connections.add_client("1234")
        self._connections.remove_client("4567", queue1)
        self.assertEqual(len(self._connections._clients["1234"]), 2, "Nonexisting client removed")
        self._connections.remove_client("1234", queue2)
        self.assertEqual(len(self._connections._clients["1234"]), 1, "Existing client not removed")

    def test_remove_all_clients(self):
        self._connections.add_client("1234")
        self._connections.add_client("4567")
        self._connections.remove_all_clients()
        self.assertEqual(len(self._connections._clients), 0, "Some clients left in collection")
        self._connections.remove_all_clients()
        self.assertEqual(len(self._connections._clients), 0, "Some clients left in collection")

    def test_send_message(self):
        queue = self._connections.add_client("1234")
        self._connections.send_message("1234", "testing message")
        self.assertEqual(queue.get_nowait(), "testing message", "Result from queue differs")
        self._connections.send_message("1234", "msg two")
        self.assertEqual(queue.get_nowait(), "msg two", "Queue has not second message")

        self._connections.send_message("51236", "random string")
        queue2 = self._connections.add_client("51236")
        self.assertEqual(queue2.get_nowait(), "random string", "Result from queue differs")
