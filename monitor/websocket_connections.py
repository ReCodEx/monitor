#!/usr/bin/env python

import asyncio
import websockets
import threading


class ClientConnections:
    """Thread safe container of futures for each connected websocket client"""

    def __init__(self):
        self.clients_ = dict()
        self.lock_ = threading.Lock()

    def get_future(self, id):
        with self.lock_:
            if id in self.clients_.keys():
                fut = self.clients_[id]
            else:
                fut = None
            return fut

    def add_client(self, id):
        with self.lock_:
            new_fut = asyncio.Future()
            self.clients_[id] = new_fut
        return new_fut

    def update_future(self, id):
        with self.lock_:
            new_fut = asyncio.Future()
            self.clients_[id] = new_fut
            return new_fut

    def remove_client(self, id):
        with self.lock_:
            if id in self.clients_.keys():
                self.clients_[id].cancel()
                del self.clients_[id]

    def remove_all_clients(self):
        with self.lock_:
            for future in self.clients_.values():
                future.cancel()
            self.clients_.clear()

    def send_message(self, id, message):
        with self.lock_:
            if id in self.clients_.keys():
                fut = self.clients_[id]
                if not fut.done():
                    fut.set_result(message)
                else:
                    # we are under heavy workload, discard this message
                    pass


def run_websock_server(connections, websock_uri, loop):
    @asyncio.coroutine
    def connection_handler(websocket, path):
        try:
            wanted_id = yield from websocket.recv()
            future = connections.add_client(wanted_id)
            yield from websocket.send("Connection established")
            while True:
                # wait for message
                yield from future
                # get message and retrieve new future
                result = future.result()
                future = connections.update_future(wanted_id)
                # send message to client
                yield from websocket.send(result)
        except websockets.ConnectionClosed:
            print("WebSocket is closed")
        except asyncio.CancelledError:
            print("Connection cancelled")

    hostname, port = websock_uri
    start_server = websockets.serve(connection_handler, hostname, port)
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_server)
    print("Server started on {}:{}".format(hostname, port))
    loop.run_forever()

