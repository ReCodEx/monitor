#!/usr/bin/env python3
"""
Script which runs the monitor - tool for resending messages from ZeroMQ to WebSockets.
"""

from monitor.websocket_connections import ClientConnections, WebsocketServer
from monitor.zeromq_connection import ServerConnection
from monitor.config_manager import ConfigManager
import asyncio
import time
import argparse


def main():
    """
    Main function of monitor program.
    :return: Nothing
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help="Path to configuration file", default=None)
    args = parser.parse_args()

    # here we'll store all active connections
    connections = ClientConnections()
    # get configuration
    config = ConfigManager(args.config)
    # create event loop for websocket server thread
    loop = asyncio.new_event_loop()

    websock_server = None
    try:
        # run websocket part of monitor in separate thread
        websock_server = WebsocketServer(config.get_websocket_uri(), connections, loop)
        websock_server.start()
        time.sleep(1)  # wait for new thread to start and print URI

        # create zeromq connection
        zmq_server = ServerConnection(*config.get_zeromq_uri())

        # specify callback for zeromq incoming message
        def message_callback(client_id, data):
            loop.call_soon_threadsafe(connections.send_message, client_id, data)
        # start zeromq server with given callback
        zmq_server.start(message_callback)
    except KeyboardInterrupt:
        pass
    finally:
        print("Quiting...")
        loop.call_soon_threadsafe(connections.remove_all_clients)
        loop.call_soon_threadsafe(loop.stop)
        if websock_server:
            websock_server.join()
        loop.close()

if __name__ == "__main__":
    main()
