import random
import socket
import json
import getopt
import sys
import time
import msgpack


class FooClient():

    def __init__(self, target_ip, port, user="anonymous", color=(0, 255, 0)):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.target_ip = target_ip
        self.port = port
        self.user = user
        self.color = color
        self.connection = None

    def connect(self):
        self.socket.connect((self.target_ip, self.port))

    def disconnect(self):
        self.socket.close()


def usage():
    pass


def run_around(steps=10):
    cmds = ["w", "a", "s", "d"]
    for i in range(0, steps):
        res = random.choice(cmds)
        print(toMsgpack(res))
        time.sleep(1)
        yield res


def opposite(direction='w'):
    if direction == 'w':
        return 's'
    elif direction == 's':
        return 'w'
    elif direction == 'a':
        return 'd'
    elif direction == 'd':
        return 'a'
    elif direction == 'b':
        return random.choice(list('wasd'))
    else:
        return '?'


def get_coordinates(msg):
    status, me = msgpack.loads(msg)
    x, y = me[2, 3]
    print(x, y, "my coordinates")


def hit_n_run(steps=20, direction='w'):
    res = None
    cmds = ["w", "a", "s", "d", "b"]
    no_run_back = [i for i in cmds if i != opposite(direction)]
    for i in range(0, steps+2):
        if i == 0:
            yield 'b'
        elif i == 1:
            yield direction
        if i < steps:
            res = random.choice(no_run_back)
            no_run_back = [i for i in cmds if i != opposite(res)]
        yield res


def parseMap(str):
    #todo
    return len(str)


def toMsgpack(command):
    if command == "w":
        return msgpack.dumps({"type": "move", "direction": "w"})
    elif command == "a":
        return msgpack.dumps({"type": "move", "direction": "a"})
    elif command == "s":
        return msgpack.dumps({"type": "move", "direction": "s"})
    elif command == "d":
        return msgpack.dumps({"type": "move", "direction": "d"})
    elif command == "c":
        return msgpack.dumps({"type": "connect", "username": "gglyptodon"})
    elif command == "m":
        #return msgpack.dumps({"type": "status", "get": "map"})
        return msgpack.dumps({"type": "map"})
    elif command == "p":
        return msgpack.dumps({"type": "points"})
    elif command == "b":
        #return msgpack.dumps({"type": "action", "set": "bomb"})
        return msgpack.dumps({"type": "bomb", "fuse_time": 1})
    elif command == "?":
        return msgpack.dumps({"type": "whoami"})

    else:
        return msgpack.dumps({"type": "whoami"})


def main():
    target_ip = '127.0.0.1' 
    port = 8001
    user = "gglyptodon"

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:],
                                       "p:t:uh",
                                       ["port=", "target=", "user", "help"])
    except getopt.GetoptError as err:
        print(str(err))
    for o, a in opts:
        if o in ("-t", "--target"):
            target_ip = a
        elif o in ("-p", "--port"):
            port = int(a)
        elif o in ("-u", "--user"):
            user = a
        elif o in ("-h", "--help"):
            usage()
        else:
            print(o)
            assert False, "unhandled option"

    fc = FooClient(target_ip=target_ip, port=port, user=user)

    try:
        fc.connect()
        fc.socket.settimeout(0.1)
        while True:
            #time.sleep(0.5)
            vars = raw_input("cmd")
            for var in list(vars):
                if var == 'q':
                    fc.disconnect()
                if var == 'm':
                    fc.socket.send(toMsgpack(var))
                    #time.sleep(0.1)
                    data = fc.socket.recv(6400)
                    map = msgpack.loads(data)
                    print(parseMap(map),"MAP")
                if var.startswith('h'):
                    tmp=list(var)
                    for c in hit_n_run(direction=random.choice(list("wasd"))):
                        print(c)
                        fc.socket.send(toMsgpack(c))
                        time.sleep(0.1)
                    try:
                        data = fc.socket.recv(6400)
                        print(msgpack.loads(data))
                    except Exception as e:
                        print(str(e))
                if var == "r":
                    for c in run_around(15):
                        fc.socket.send(toMsgpack(c))
                        #time.sleep(1)
                    try:
                        data = fc.socket.recv(6400)
                        print(msgpack.loads(data))
                    except Exception as e:
                        print(str(e))
                if not vars:
                    var = "?"
                msg = toMsgpack(var)
                fc.socket.send(msg)
                try:
                    data = fc.socket.recv(6400)
                    print(msgpack.loads(data))
                except Exception as e:
                    print(str(e))
    except Exception as e:
        print(e)
        fc.disconnect()


if __name__ == "__main__":
    main()
