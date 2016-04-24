#!/usr/bin/env python3

import yaml


class ConfigManager:
    """
    Class to handle all configuration items.
    """
    def __init__(self, config_file=None):
        """
        Init with default values.
        :param config_file: Path to YAML configuration file.
        If not given, default values are used.
        """

        self._config = dict()
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    self._config = yaml.safe_load(f)
            except FileNotFoundError:
                # using defaults
                pass

    def get_websocket_uri(self):
        """
        Get address for websocket server.
        :return: List with 2 items - string hostname and int port
        """
        return self._config['websocket_uri'] if 'websocket_uri' in self._config else ['127.0.0.1', 4567]

    def get_zeromq_uri(self):
        """
        Get address for zeromq server.
        :return: List with 2 items - string hostname and int port
        """
        return self._config['zeromq_uri'] if 'zeromq_uri' in self._config else ['127.0.0.1', 7894]

    def get_logger_path(self):
        """
        Get path to system log file.
        :return: String representation of path to file.
        """
        return self._config['logger_path'] if 'logger_path' in self._config else '/tmp/recodex-monitor.log'
