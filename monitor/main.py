#!/usr/bin/env python
"""
Script which runs the monitor - tool for resending messages from ZeroMQ to WebSockets.
"""

from monitor import websocket_connections as wc
from monitor import config_manager as cm
import threading
import asyncio
import time


def main(argv=None):
    # here we'll store all active connections
    connections = wc.ClientConnections()
    # get configuration
    config = cm.ConfigManager()
    # create event loop for websocket server thread
    loop = asyncio.new_event_loop()

    websock_thread = None
    try:
        websock_thread = threading.Thread(target=wc.run_websock_server,
                                          args=(connections, config.get_websocket_uri(), loop))
        websock_thread.start()
        time.sleep(1)  # wait for new thread to start and print URI
        while True:
            text = input("> ")
            if text == "exit":
                break
            loop.call_soon_threadsafe(connections.send_message, "1234", text)
    except KeyboardInterrupt:
        pass
    finally:
        print("Quiting...")
        loop.call_soon_threadsafe(connections.remove_all_clients)
        loop.call_soon_threadsafe(loop.stop)
        if websock_thread:
            websock_thread.join()
        loop.close()

if __name__ == "__main__":
    main()
