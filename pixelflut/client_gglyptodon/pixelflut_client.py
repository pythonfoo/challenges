import socket
import json
import random
import getopt
import sys


class FooClient():

    def __init__(self, target_ip, port, user="anonymous", color=(0, 255, 0)):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.target_ip = target_ip
        self.port = port
        self.user = user
        self.color = color

    def send_msg(self, user=None, x=None, y=None, color=(255, 255, 255)):
        self.socket.connect((self.target_ip, self.port))
        if x is None or y is None:
            msg = json.dumps({'user': self.user, 'x': random.randint(0, 1024),
                              'y': random.randint(0, 768), 'color': self.color})
        else:
            msg = json.dumps({'user': user, 'x': x, 'y': y, 'color': color})
        self.socket.send(msg)
        data = self.socket.recv(1024)
        print(data, "received")
        self.socket.close()


def usage():
    print("""
    python pixelflut_client.py -x 100 -X 160 -y 220 -Y 290
    """)
    sys.exit(1)


def main():
    x1 = 0
    y1 = 0
    x2 = 600
    y2 = 1024
    target_ip = '127.0.0.1'
    port = 9999
    user = "gglyptodon"
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:],
                                       "t:p:u:x:X:y:Y:h",
                                       ["target=", "port=", "user", "x_top=", "x_bottom=", "y_left=", "y_right=", "help"])
    except getopt.GetoptError as err:
        print(str(err))
    for o, a in opts:
        if o in ("-x", "--x_top"):
            x1 = int(a)
        elif o in ("-X", "--x_bottom"):
            x2 = int(a)
        elif o in ("-y", "--y_left"):
            y1 = int(a)
        elif o in ("-Y", "--y_right"):
            y2 = int(a)
        elif o in ("-t", "--target"):
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

    painted = set()
    while 1:
        xval = random.randint(x1, x2)
        yval = random.randint(y1, y2)
        if not str(xval)+","+str(yval) in painted:
            FooClient(target_ip=target_ip, port=port, user=user).send_msg(x=xval, y=yval, color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            painted.add(str(xval)+","+str(yval))

if __name__ == "__main__":
    main()
