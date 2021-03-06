# vim:ts=4:sts=4:sw=4:expandtab

import errno
from collections import deque
from _multiprocessing import Connection
from satori.objects import Argument
from .protocol import Attach, Detach, Disconnect, Map, Unmap, Send, Receive, KeepAlive, ProtocolError

class Slave2(object):
    @Argument('connection', type=Connection)
    def __init__(self, connection):
        self.connection = connection
        self.queue_clients = dict()
        self.clients = set()
        self.added_clients = deque()
        self.removed_clients = deque()
        self.terminated = False

    def terminate(self):
        self.terminated = True

    def attach(self, client, queue):
        if queue not in self.queue_clients:
            self.connection.send(Attach(queue))
            self.connection.recv()
            self.queue_clients[queue] = deque()
        self.queue_clients[queue].append(client)

    def detach(self, client, queue):
        if queue in self.queue_clients:
            self.queue_clients[queue].remove(client)
            if not self.queue_clients[queue]:
                self.connection.send(Detach(queue))
                self.connection.recv()
                del self.queue_clients[queue]

    def map(self, criteria, queue):
        self.connection.send(Map(criteria, queue))
        return self.connection.recv()

    def unmap(self, mapping):
        self.connection.send(Unmap(mapping))
        self.connection.recv()

    def send(self, event):
        self.connection.send(Send(event))
        self.connection.recv()

    def keep_alive(self):
        self.connection.send(KeepAlive())
        self.connection.recv()

    def disconnect(self):
        self.connection.send(Disconnect())

    def add_client(self, client):
        self.added_clients.append(client)

    def remove_client(self, client):
        self.removed_clients.append(client)

    def run(self):
        try:
            while not self.terminated:
                while self.removed_clients:
                    client = self.removed_clients.popleft()
                    for queue in set(self.queue_clients):
                        if client in self.queue_clients[queue]:
                            self.detach(client, queue)
                    client.deinit()
                    self.clients.remove(client)

                while self.added_clients:
                    client = self.added_clients.popleft()
                    self.clients.add(client)
                    client.slave = self
                    client.init()

                if not self.clients:
                      break
                
                self.connection.send(Receive())

                try:
                    (queue, event) = self.connection.recv()
                except IOError as e:
                    if e[0] == errno.EINTR:
                        break
                    else:
                        raise

                if queue in self.queue_clients:
                    client = self.queue_clients[queue].popleft()
                    client.handle_event(queue, event)
                    self.queue_clients[queue].append(client)
        finally:
            # not deinitializing remaining clients, only disconnecting from queues
            for client in self.clients:
                for queue in set(self.queue_clients):
                    if client in self.queue_clients[queue]:
                        self.detach(client, queue)

            self.clients.clear()

        self.disconnect()

