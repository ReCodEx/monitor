#!/usr/bin/env python3

import tempfile
import unittest
import os
from monitor.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    def test_websock_uri_default(self):
        config = ConfigManager()
        self.assertEqual(config.get_websocket_uri(), ["127.0.0.1", 4567])

        # wrong filename - using defaults
        config = ConfigManager('/a/b/tmp/log.bla')
        self.assertEqual(config.get_websocket_uri(), ["127.0.0.1", 4567])

    def test_websock_uri_loaded(self):
        handle, path = tempfile.mkstemp()
        with open(path, 'w') as f:
            f.write('websocket_uri:\n  - 77.75.76.3\n  - 8080')

        config = ConfigManager(path)
        self.assertEqual(config.get_websocket_uri(), ["77.75.76.3", 8080])
        os.remove(path)

    def test_zeromq_uri_default(self):
        config = ConfigManager()
        self.assertEqual(config.get_zeromq_uri(), ["127.0.0.1", 7894])

        # wrong filename - using defaults
        config = ConfigManager('/a/b/tmp/log.bla')
        self.assertEqual(config.get_zeromq_uri(), ["127.0.0.1", 7894])

    def test_zeromq_uri_loaded(self):
        handle, path = tempfile.mkstemp()
        with open(path, 'w') as f:
            f.write('zeromq_uri:\n  - 77.75.76.3\n  - 8080')

        config = ConfigManager(path)
        self.assertEqual(config.get_zeromq_uri(), ["77.75.76.3", 8080])
        os.remove(path)

    def test_logger_path_default(self):
        config = ConfigManager()
        self.assertEqual(config.get_logger_path(), "/tmp/recodex-monitor.log")

        # wrong filename - using defaults
        config = ConfigManager('/a/b/tmp/log.bla')
        self.assertEqual(config.get_logger_path(), "/tmp/recodex-monitor.log")

    def test_logger_path_loaded(self):
        handle, path = tempfile.mkstemp()
        with open(path, 'w') as f:
            f.write('logger_path: /var/log/tmp/file.log')

        config = ConfigManager(path)
        self.assertEqual(config.get_logger_path(), "/var/log/tmp/file.log")
        os.remove(path)
