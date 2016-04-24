#!/usr/bin/env python

import unittest
from monitor import config_manager as cm


class TestConfigManager(unittest.TestCase):
    def test_websock_uri(self):
        config = cm.ConfigManager()
        self.assertEqual(config.get_websocket_uri(), ("localhost", 4567))

    def test_zeromq_uri(self):
        config = cm.ConfigManager()
        self.assertEqual(config.get_zeromq_uri(), ("127.0.0.1", 7894))
