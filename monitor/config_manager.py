#!/usr/bin/env python


class ConfigManager:
    def __init__(self):
        self.websocket_hostname_ = "localhost"
        self.websocket_port_ = 4567
        self.zeromq_hostname_ = "localhost"
        self.zeromq_port_ = 7894

    def get_websocket_uri(self):
        return self.websocket_hostname_, self.websocket_port_

    def get_zeromq_uri(self):
        return self.zeromq_hostname_, self.zeromq_port_
