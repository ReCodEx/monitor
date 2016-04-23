#!/usr/bin/env python

import unittest
import asyncio
from monitor import websocket_connections as wc


class TestClientConnections(unittest.TestCase):
    def setUp(self):
        self._connections = wc.ClientConnections()

    def test_add_client(self):
        fut = self._connections.add_client("1234")
        self.assertNotEqual(fut, None, "No future returned")
        self.assertIsInstance(fut, asyncio.Future, "Wrong type of returned value")
        self.assertFalse(fut.done(), "Future is already filled")
        self.assertEqual(fut, self._connections._clients["1234"],
                         "Future not present at requested id")
        fut2 = self._connections.add_client("456777")
        self.assertNotEqual(fut, fut2, "Different clients have same future")

    def test_update_future(self):
        prev_fut = self._connections.add_client("1234")
        new_fut = self._connections.update_future("1234")
        self.assertNotEqual(prev_fut, new_fut, "Updated future is not new")
        self.assertIsInstance(new_fut, asyncio.Future, "Wrong type of returned value")
        self.assertFalse(new_fut.done(), "Future is already filled")
        self.assertEqual(new_fut, self._connections._clients["1234"],
                         "Future not present at requested id")

    def test_remove_client(self):
        fut = self._connections.add_client("1234")
        self._connections.remove_client("4567")
        self.assertEqual(len(self._connections._clients), 1, "Nonexisting client removed")
        self._connections.remove_client("1234")
        self.assertEqual(len(self._connections._clients), 0, "Existing client not removed")
        self.assertTrue(fut.cancelled(), "Future not cancelled")

    def test_remove_all_clients(self):
        fut1 = self._connections.add_client("1234")
        fut2 = self._connections.add_client("4567")
        self._connections.remove_all_clients()
        self.assertEqual(len(self._connections._clients), 0, "Some clients left in collection")
        self.assertTrue(fut1.cancelled(), "Future not cancelled")
        self.assertTrue(fut2.cancelled(), "Future not cancelled")
        self._connections.remove_all_clients()
        self.assertEqual(len(self._connections._clients), 0, "Some clients left in collection")

    def test_send_message(self):
        fut = self._connections.add_client("1234")
        ret = self._connections.send_message("1234", "testing message")
        self.assertTrue(ret, "Message not sent")
        self.assertTrue(fut.done())
        self.assertEqual(fut.result(), "testing message", "Future result differs")
        ret2 = self._connections.send_message("1234", "msg two")
        self.assertFalse(ret2, "Message sent when future already filled")
        self.assertEqual(fut.result(), "testing message", "Future changed value")
        ret3 = self._connections.send_message("51236", "random string")
        self.assertFalse(ret3, "Message sent to nonexisting host id")


if __name__ == '__main__':
    unittest.main()
