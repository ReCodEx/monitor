#!/usr/bin/env python3
"""
Classes and functions for websocket connections and message sending
"""

import asyncio
import websockets
import threading


class ClientConnections:
    """
    Container for managing connected websocket clients. Messages are passed as
    asyncio.Future values, so all methods must be called from the same thread
    (event loop) as main websocket connection handler. Thus this class is not
    thread safe.
    """

    def __init__(self, logger):
        """
        Initialize empty client dictionary
        """
        self._clients = dict()
        self._logger = logger

    def add_client(self, id):
        """
        Register new client which wants to receive messages to identifier 'id'.
        Only one subscriber per stream is allowed. Latter overrides previous one.

        :param id: Identifier of required stream of messages
        :return: Returns new asyncio.Future on which can be wait for by
            'yield from' command.
        """
        new_fut = asyncio.Future()
        self._clients[id] = new_fut
        self._logger.debug("client connection: new client '{}' registered".format(id))
        return new_fut

    def update_future(self, id):
        """
        Update future for message stream with 'id' identifier. This should be
        called after one message was sent (previous future was filled).

        :param id: Identifier of required stream of messages
        :return: Returns new asyncio.Future
        """
        new_fut = asyncio.Future()
        self._clients[id] = new_fut
        self._logger.debug("client connection: future for client '{}' updated".format(id))
        return new_fut

    def remove_client(self, id):
        """
        Remove client listening on 'id' message stream. This means cancelling
        underlying future and deleting the entry from internal dictionary.
        If no such client exists, nothing is done.

        :param id: Identifier of required stream of messages
        :return: Nothing
        """
        if id in self._clients.keys():
            self._clients[id].cancel()
            del self._clients[id]
            self._logger.debug("client connection: client '{}' removed".format(id))
        else:
            self._logger.debug("client connection: client '{}' removing failed - "
                               " not present".format(id))

    def remove_all_clients(self):
        """
        Remove all registered clients. This method could be called on app
        shutdown or when incoming connection is lost.

        :return: Nothing
        """
        for future in self._clients.values():
            future.cancel()
        self._clients.clear()
        self._logger.debug("client connection: all clients removed")

    def send_message(self, id, message):
        """
        Send 'message' to client listening on stream with 'id'. If 'id' is not
        known, the message is silently dropped. If last message to this 'id' was
        not already sent, this message is also dropped to save resources.

        :param id: Identifier of required stream of messages
        :param message: String containing text to be sent
        :return: Returns True if message was sent, False otherwise
        """
        if id in self._clients.keys():
            fut = self._clients[id]
            if not fut.done():
                fut.set_result(message)
                return True
            else:
                # we are under heavy workload, discard this message
                self._logger.warning("client connection: Dropping message '{}' for "
                                     "stream '{}' because previous one was not yet "
                                     "processed".format(message, id))
        else:
            self._logger.warning("client connection: Dropping message '{}' for "
                                 "non-existing stream '{}'".format(message, id))
        return False


class WebsocketServer(threading.Thread):
    """
    Websocket server, which handles all connection asynchronously in one
    (separate) thread. To start server, call start() method, for waiting to
    finish, there is join() method (as in threading.Thread class).
    """

    def __init__(self, websock_uri, connections, loop, logger):
        """
        Initialize new instance

        :param websock_uri: Tuple containing hostname and port for websocket server
        :param connections: Reference to ClientConnections class through which are
            sent messages from other threads. Note, that this must be invoked thread
            safe via given message loop of asyncio module.
        :param loop: Asyncio message loop for handling connections
        :param logger: System logger instance
        """
        super().__init__()
        self._connections = connections
        self._loop = loop
        self._logger = logger
        hostname, port = websock_uri
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self.connection_handler, hostname, port)
        loop.run_until_complete(start_server)
        self._logger.info("websocket server initialized at {}:{}".format(hostname, port))

    @asyncio.coroutine
    def connection_handler(self, websocket, path):
        """
        Internal asyncio.coroutine function for handling one websocket request.

        :param websocket: Socket with request
        :param path: Requested path of socket (not used)
        :return: Returns when socket is closed or future from ClientConnections
            is cancelled.
        """
        wanted_id = None
        try:
            wanted_id = yield from websocket.recv()
            future = self._connections.add_client(wanted_id)
            self._logger.debug("websocket server: got client for channel '{}'".format(wanted_id))
            yield from websocket.send("Connection established")
            while True:
                # wait for message
                yield from future
                # get message and retrieve new future
                result = future.result()
                self._logger.debug("websocket server: message '{}' for channel '{}'".format(result, wanted_id))
                future = self._connections.update_future(wanted_id)
                # send message to client
                yield from websocket.send(result)
                self._logger.debug("websocket server: message sent to channel '{}'".format(wanted_id))
        except websockets.ConnectionClosed:
            self._logger.info("websocket server: connection closed for channel '{}'". format(wanted_id))
        except asyncio.CancelledError:
            self._logger.error("websocket server: connection cancelled for channel '{}'".format(wanted_id))
        finally:
            self._connections.remove_client(wanted_id)

    def run(self):
        """
        Function to start websocket server, which handle and serve all connections.

        :return: This function returns when given message loop is stopped and returns
            nothing.
        """
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

