#! /usr/bin/env python3
""" bomber.py

a little server where you can send commands to paint a specific pixel.

Usage:

    bomber.py
"""
import pygame
import pygame.locals
import asyncio
import time
import json
from docopt import docopt


class JsonUnpacker:

    def __init__(self, encoding='utf-8'):
        self.encoding = encoding
        self.buffer = ""

    def feed(self, next_bytes):
        self.buffer += str(next_bytes, "utf-8")

    def __iter__(self):
        return self

    def next(self):
        if self.buffer and self.buffer[0] != "{":
            #dump everything until the next {
            next_start = self.buffer.find("{")
            if next_start > 0:
                self.buffer = self.buffer[next_start:]
            else:
                self.buffer = ""

        next_stop = self.buffer.find("}")
        if self.buffer == "" or next_stop < 0:
            raise StopIteration("No more data to unpack")

        jsonstr = self.buffer[:next_stop+1]
        self.buffer = self.buffer[next_stop+1:]
        return json.loads(jsonstr)

    __next__ = next


class ClientStub:

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.peername = None


class Server:

    """
    took the structure from
    https://github.com/Mionar/aiosimplechat
    it was MIT licenced
    """
    clients = {}
    server = None

    def __init__(self, host='*', port=8001):
        self.host = host
        self.port = port
        self.clients = {}

    @asyncio.coroutine
    def run_server(self):
        try:
            self.server = yield from asyncio.start_server(
                self.client_connected,
                self.host, self.port
            )
            print('Running server on {}:{}'.format(self.host, self.port))
        except OSError:
            print('Cannot bind to this port! Is the server already running?')

    def send_to_client(self, peername, msg):
        client = self.clients[peername]
        client.writer.write(bytes(json.dumps(msg), "utf-8"))
        return

    def send_to_all_clients(self, msg):
        for peername in self.clients.keys():
            self.send_to_client(peername, msg)
        return

    def close_clients(self):
        for peername, client in self.clients.items():
            client.writer.write_eof()

    @asyncio.coroutine
    def client_connected(self, reader, writer):
        peername = writer.transport.get_extra_info('peername')
        new_client = ClientStub(reader, writer)
        self.clients[peername] = new_client
        # self.send_to_client(peername, 'Welcome {}'.format(peername))
        unpacker = JsonUnpacker(encoding='utf-8')
        while not reader.at_eof():
            try:
                pack = yield from reader.read(1024)
                unpacker.feed(pack)
                for msg in unpacker:
                    handle_msg(msg)
            except ConnectionResetError as e:
                print('ERROR: {}'.format(e))
                del self.clients[peername]
                return
            except Exception as e:
                error = 'ERROR: {}'.format(e)
                print(error)
                self.send_to_client(peername, error)
                new_client.writer.write_eof()
                del self.clients[peername]
                raise
                return
            self.send_to_client(peername, "OK\n")

    def close(self):
        self.send_to_all_clients("bye\n")
        self.close_clients()


@asyncio.coroutine
def main_loop(loop):
    now = last = time.time()

    while True:
        # 30 frames per second, considering computation/drawing time
        last, now = now, time.time()
        time_per_frame = 1 / 30
        yield from asyncio.sleep(last + time_per_frame - now)

        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                return

        # DRAWING
        pygame.display.flip()


def handle_msg(msg):
    user = msg["user"]
    pos = msg["x"], msg["y"]
    color = msg["color"]
    pygame.draw.line(screen, color, pos, pos)


if __name__ == "__main__":
    arguments = docopt(__doc__, version='helangor 0.8')

    loop = asyncio.get_event_loop()
    pygame.init()
    screen = pygame.display.set_mode((900, 700))
    if not arguments.get('--connect'):
        gameserver = Server()
        asyncio.async(gameserver.run_server())

    try:
        loop.run_until_complete(main_loop(loop))
    finally:
        loop.close()
