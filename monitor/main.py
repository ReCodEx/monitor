#!/usr/bin/env python3
"""
Script which runs the monitor - tool for resending messages from ZeroMQ to WebSockets.
"""

from .websocket_connections import ClientConnections, WebsocketServer
from .zeromq_connection import ServerConnection
from .config_manager import ConfigManager, init_logger
import asyncio
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', help="Path to configuration file", default=None)


def main():
    """
    Main function of monitor program.

    :return: Nothing
    """
    args = parser.parse_args()

    # get configuration
    config = ConfigManager(args.config)
    # create event loop for websocket server thread
    loop = asyncio.new_event_loop()
    # get logger
    logger = init_logger(*config.get_logger_settings())
    # here we'll store all active connections
    connections = ClientConnections(logger)

    websock_server = None
    try:
        logger.info("starting websocket server ...")
        # run websocket part of monitor in separate thread
        websock_server = WebsocketServer(config.get_websocket_uri(), connections, loop, logger)
        websock_server.start()
        logger.info("websocket server started")

        # create zeromq connection
        logger.info("starting zeromq server ...")
        zmq_uri = config.get_zeromq_uri()
        zmq_server = ServerConnection(zmq_uri[0], zmq_uri[1], logger)

        # specify callback for zeromq incoming message
        def message_callback(client_id, data):
            loop.call_soon_threadsafe(connections.send_message, client_id, data)
        # start zeromq server with given callback
        zmq_server.start(message_callback)
    except KeyboardInterrupt:
        logger.warning("keyboard interrupt detected")
    finally:
        logger.warning("quiting...")
        loop.call_soon_threadsafe(connections.remove_all_clients)
        logger.debug("websocket clients removed")
        loop.call_soon_threadsafe(loop.stop)
        logger.debug("websocket message loop stopped")
        if websock_server:
            websock_server.join()
            logger.debug("websocket server thread exited")
        loop.close()
        logger.debug("main thread exited")

if __name__ == "__main__":
    main()
