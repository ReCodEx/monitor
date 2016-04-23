#!/usr/bin/env python3


class ConfigManager:
    """
    Class to handle all configuration items.
    """
    def __init__(self):
        """
        Init with default values.
        """
        self.websocket_address_ = "localhost"
        self.websocket_port_ = 4567
        self.zeromq_address_ = "127.0.0.1"
        self.zeromq_port_ = 7894

    def get_websocket_uri(self):
        """
        Get address for websocket server.
        :return: Tuple with address and port (both strings)
        """
        return self.websocket_address_, self.websocket_port_

    def get_zeromq_uri(self):
        """
        Get address for zeromq server.
        :return: Tuple with address and port (both strings)
        """
        return self.zeromq_address_, self.zeromq_port_
