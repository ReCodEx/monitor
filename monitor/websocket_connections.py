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
    asyncio.Queue item values, so all methods must be called from the same thread
    (event loop) as main websocket connection handler. Thus this class is not
    thread safe.
    """

    def __init__(self, logger, loop):
        """
        Initialize empty client dictionary

        :param logger: System logger.
        :param loop: Main asyncio event loop.
        """
        self._clients = dict()
        self._saved_messages = dict()
        self._logger = logger
        self._loop = loop

    def add_client(self, id):
        """
        Register new client which wants to receive messages to identifier 'id'.
        If there are any such messages, they are sent immediately. There can be
        more subscribers per stream.

        :param id: Identifier of required stream of messages
        :return: Returns new asyncio.Queue on which can be wait for by
            'yield from' command.
        """
        new_queue = asyncio.Queue()
        if id not in self._clients.keys():
            self._clients[id] = []
        self._clients[id].append(new_queue)

        # if there are already any messages, send them
        if id in self._saved_messages.keys():
            for msg in self._saved_messages[id]:
                new_queue.put_nowait(msg)

        self._logger.debug("client connection: new client '{}' registered".format(id))
        return new_queue

    def remove_channel(self, id):
        """
        Remove all clients listening on 'id' channel. This means removing all associated
        queues and received messages. If no such channel exists, nothing is done.
        This method is called 5 minutes after last message of each channel.

        :param id: Identifier of required stream of messages
        :return: Nothing
        """
        if id in self._saved_messages.keys():
            del self._saved_messages[id]

        if id in self._clients.keys():
            del self._clients[id]
            self._logger.debug("client connection: channel '{}' removed".format(id))
        else:
            self._logger.debug("client connection: channel '{}' removing failed - "
                               " not present".format(id))

    def remove_client(self, id, queue):
        """
        Remove client listening on 'id' message stream with queue 'queue'.
        This means removing associated queue and deleting the entry from internal dictionary.
        If no such client exists, nothing is done.

        :param id: Identifier of required stream of messages
        :param queue: Queue associated with client to be removed
        :return: Nothing
        """
        if id in self._clients.keys():
            clients = self._clients[id]
            clients.remove(queue)
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
        self._clients.clear()
        self._saved_messages.clear()
        self._logger.debug("client connection: all clients removed")

    def send_message(self, id, message):
        """
        Send 'message' to client listening on stream with 'id'. If 'id' is not
        known, the message is saved for latter use. Messages for connected
        clients are put into queues, so no message will get lost.

        :param id: Identifier of required stream of messages
        :param message: String containing text to be sent
        :return: Nothing
        """

        if id not in self._saved_messages.keys():
            self._saved_messages[id] = []
        self._saved_messages[id].append(message)

        if id in self._clients.keys():
            for queue in self._clients[id]:
                queue.put_nowait(message)

        # on last message schedule removing whole channel after 5 minute wait
        if message is None:
            self._loop.call_later(5*60, self.remove_channel, id)


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
        :return: Returns when socket is closed or poison pill is found in message queue
            from ClientConnections.
        """
        wanted_id = None
        queue = None
        try:
            wanted_id = yield from websocket.recv()
            queue = self._connections.add_client(wanted_id)
            self._logger.info("websocket server: got client for channel '{}'".format(wanted_id))
            while True:
                # wait for message
                result = yield from queue.get()
                if not result:
                    break
                self._logger.debug("websocket server: message '{}' for channel '{}'".format(result, wanted_id))
                # send message to client
                yield from websocket.send(result)
                self._logger.debug("websocket server: message sent to channel '{}'".format(wanted_id))
        except websockets.ConnectionClosed:
            if wanted_id:
                self._logger.info("websocket server: connection closed for channel '{}'". format(wanted_id))
        finally:
            if wanted_id and queue:
                self._connections.remove_client(wanted_id, queue)


    def run(self):
        """
        Function to start websocket server, which handle and serve all connections.

        :return: This function returns when given message loop is stopped and returns
            nothing.
        """
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

