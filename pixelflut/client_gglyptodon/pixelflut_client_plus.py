from multiprocessing import Process
import random
import getopt
import sys
import json
import socket
from PIL import Image

class FooClient():

    def __init__(self, target_ip, port, user="anonymous", color=(0, 255, 0)):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.target_ip = target_ip
        self.port = port
        self.user = user
        self.color = color

    def send_msg(self, user=None, x=None, y=None, color=(255, 255, 255)):
        print("MSG")
        self.socket.connect((self.target_ip, self.port))
        if x is None or y is None:
            msg = json.dumps({'user': self.user, 'x': random.randint(0, 1024),
                              'y': random.randint(0, 768), 'color': self.color})
            print(msg)
        else:
            msg = json.dumps({'user': user, 'x': x, 'y': y, 'color': color})
            print(msg)
        self.socket.send(msg)
        data = self.socket.recv(1024)
        print(data, "received")
        self.socket.close()


def get_img_dim(imgfile):
    global imgdict
    im = imgdict[imgfile]
    return im.size


class ImageDict(dict):
    def __missing__(self, key):
        self[key] = img = self.load(key)
        return img
    def load(self, key):
        img = Image.open(key)
        return img


def paint_img(imgfile,fooclient=FooClient(target_ip='127.0.0.1', port=8001), mode = None,xstart=None, xend=None,ystart=None,yend=None):
    global painted
    global vertical
    global imgdict
    global pixelpool
    if not mode:
        mode = random.randint(0,7)
    max_x, max_y =  get_img_dim(imgfile)

    if not xstart or xstart >= max_x:
        xstart = random.randint(0,max_x)
    if not ystart or ystart >= max_y:
        ystart = random.randint(0,max_y)
    if not xend:
        xend = max_x
    if not yend:
        yend = max_y

    im = imgdict[imgfile]
    rgb_pixmat = im.load()
    if mode == 0: #vertical
        for i in range(xstart,xend):
           for j in range(ystart,yend):
               if not str(i)+","+str(j) in painted:
                    #print("painting",i, j, rgb_pixmat[i,j] )
                    newfoo = FooClient(port=fooclient.port, target_ip=fooclient.target_ip, user=fooclient.user)
                    newfoo.send_msg(user="bla",x=i, y=j, color=rgb_pixmat[i,j])
                    painted.add(str(i)+","+str(j))
    elif mode == 1: #hor
        for i in range(ystart,yend):
           for j in range(xstart,xend):
               if not str(i)+","+str(j) in painted:
                    #print("painting",i, j, rgb_pixmat[i,j] )
                    newfoo = FooClient(port=fooclient.port, target_ip=fooclient.target_ip, user=fooclient.user)
                    newfoo.send_msg(user="bla",x=j, y=i, color=rgb_pixmat[j,i])
                    painted.add(str(j)+","+str(i))
    elif mode == 2: #both
        for i in range(xstart,xend):
           for j in range(ystart,yend):
               if not str(i)+","+str(j) in painted:
                    #print("painting",i, j, rgb_pixmat[i,j] )
                    FooClient(port=fooclient.port, target_ip=fooclient.target_ip,
                                       user=fooclient.user).send_msg(user="bla",x=i, y=j, color=rgb_pixmat[i,j])
                    if i < max_y and j < max_x:
                        if not str(j)+","+str(i) in painted:
                            FooClient(port=fooclient.port, target_ip=fooclient.target_ip, user=fooclient.user).send_msg(user="bla",x=j, y=i, color=rgb_pixmat[j,i])
                            painted.add(str(j)+","+str(i))
    elif mode == 3:
        for i in reversed(range(random.randint(0,max_x-(max_x/5)),max_x)):
           for j in reversed(range(0, max_y)):
               if not str(i)+","+str(j) in painted:
                    #print("painting",i, j, rgb_pixmat[i,j] )
                    FooClient(port=fooclient.port, target_ip=fooclient.target_ip,
                                       user=fooclient.user).send_msg(user="bla",x=i, y=j, color=rgb_pixmat[i,j])
                    painted.add(str(j)+","+str(i))
                    if i < max_y and j < max_x:
                        if not str(j)+","+str(i) in painted:
                            FooClient(port=fooclient.port, target_ip=fooclient.target_ip,
                                       user=fooclient.user).send_msg(user="bla",x=j, y=i, color=rgb_pixmat[j,i])
                            painted.add(str(j)+","+str(i))
    elif mode == 4:
        print(max_x, max_y)
        print(len(pixelpool))
        for i in scrambled(range(0,max_y)):
            tmp = pixelpool.pop(random.randint(0,len(pixelpool)-1))
            for j in tmp:
            #print(j)
            #print(i,j)
            #print(rgb_pixmat[i,j])
                if not str(i)+","+str(j) in painted:
                    FooClient(port=fooclient.port, target_ip=fooclient.target_ip,
                                         user=fooclient.user).send_msg(user="bla",x=j, y=i, color=rgb_pixmat[j,i])
                    painted.add(str(i)+","+str(j))







def usage():
    print("""
    python pixelflut_client.py -x 100 -X 160 -y 220 -Y 290
    """)
    sys.exit(1)


painted = set()
vertical  = False
horizontal = False
both = True
imgdict = ImageDict()
pixelpool = []


def scrambled(orig):
    dest = orig[:]
    random.shuffle(dest)
    return dest


def main():
    x1 = 0
    y1 = 0
    x2 = 600
    y2 = 1024
    target_ip = '127.0.0.1'
    port = 8001
    user = "gglyptodon"
    img = None #"/home/nin/Desktop/tesla.jpg"
    global pixelpool
    global painted




    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:],
                                       "i:t:p:u:x:X:y:Y:h",
                                       ["image=","target=", "port=", "user", "x_top=", "x_bottom=", "y_left=", "y_right=", "help"])
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
        elif o in ("-i", "--image"):
            img = a
        elif o in ("-h", "--help"):
            usage()
        else:
            print(o)
            assert False, "unhandled option"


    while not img:
        xval = random.randint(x1, x2)
        yval = random.randint(y1, y2)
        if not str(xval)+","+str(yval) in painted:
            FooClient(target_ip=target_ip, port=port, user=user).send_msg(x=xval, y=yval, color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            painted.add(str(xval)+","+str(yval))


    width,height = get_img_dim(img)

    for i in range(0,height):
        pixelpool.append(scrambled(range(0,width)))

    for i in range(0,50):
        p = Process(target=paint_img, kwargs={"mode":None,"fooclient":FooClient(target_ip=target_ip, port=port, user=user), "imgfile":img,"xstart":None,"xend":None,"ystart":None,"yend":None })
        p.start()




if __name__ == "__main__":
    main()
