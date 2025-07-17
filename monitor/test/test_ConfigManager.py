#!/usr/bin/env python3

import tempfile
import unittest
import os
import logging
from monitor.config_manager import ConfigManager, init_logger


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
        self.assertEqual(config.get_logger_settings(), ["/tmp/recodex-monitor.log", logging.INFO, 1024*1024, 3])

        # wrong filename - using defaults
        config = ConfigManager('/a/b/tmp/log.bla')
        self.assertEqual(config.get_logger_settings(), ["/tmp/recodex-monitor.log", logging.INFO, 1024*1024, 3])

    def test_logger_path_loaded(self):
        handle, path = tempfile.mkstemp()
        with open(path, 'w') as f:
            f.write('logger:\n  file: /var/log/tmp/file.log\n  level: "debug"\n  max-size: 564\n  rotations: 7')

        config = ConfigManager(path)
        self.assertEqual(config.get_logger_settings(), ["/var/log/tmp/file.log", logging.DEBUG, 564, 7])
        os.remove(path)

    def test_loglevel_from_string(self):
        config = ConfigManager()
        self.assertEqual(config._get_loglevel_from_string("debug"), logging.DEBUG)
        self.assertEqual(config._get_loglevel_from_string("info"), logging.INFO)
        self.assertEqual(config._get_loglevel_from_string("warning"), logging.WARNING)
        self.assertEqual(config._get_loglevel_from_string("error"), logging.ERROR)
        self.assertEqual(config._get_loglevel_from_string("critical"), logging.CRITICAL)
        self.assertEqual(config._get_loglevel_from_string("nonexisting"), logging.INFO)


class TestLoggerInitialization(unittest.TestCase):
    def test_invalid_path(self):
        logger = init_logger("/a/b/c.txt", logging.INFO, 45, 2)
        self.assertFalse(logger.isEnabledFor(logging.CRITICAL))
        # restore global logging
        logging.disable(logging.NOTSET)

    def test_valid_creation(self):
        handle, path = tempfile.mkstemp()
        logger = init_logger(path, logging.WARNING, 450, 2)
        logger.debug("aaa")
        logger.warning("bbb")
        logger.error("ccc")
        [h.flush() for h in logger.handlers]

        self.assertEqual(logger.getEffectiveLevel(), logging.WARNING)
        with open(path, 'r') as f:
            content = f.readlines()
            # expect 5 lines - 3 of header and one with 'bbb' and one 'ccc'
            self.assertEqual(len(content), 5)

        os.remove(path)
