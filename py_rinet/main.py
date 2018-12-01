
# -*- coding:utf-8 -*-
from listener import Listen
from ioloop import IoLoop
import sys
import os
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(path)

class PORTERROR(Exception):
    def __init__(self,port):
        self.port = port
    def __str__(self):
        return "port {} illegal".format(self.port)
class HOSTERROR(Exception):
    def __init__(self,host):
        self.host = host
    def __str__(self):
        return "host {} illegal".format(self.host)
def check_port(port):
    if port <= 0 or port >= 65535:
        PORTERROR(port)

def check_host(host):
    bs = host.split(".")
    if len(bs) != 4 :
        raise HOSTERROR(host)
    for b in bs :
        if int(b) <0 or int(b) >255:
            raise HOSTERROR(host+":"+b)

if __name__ == "__main__":
    argv = sys.argv
    if len(argv) != 5 :
        print "un support argv , check it please"
    bind_host     = argv[1]
    bind_port     = int(argv[2])
    target_host   = argv[3]
    target_port   = int(argv[4])
    check_host(target_host)
    check_host(bind_host)
    check_port(target_port)
    check_port(bind_port)
    listener = Listen(bind_host,bind_port, target_host,target_port)
    listener.start_listen()
    IoLoop.instance().start()

"""
main.py 0.0.0.0 9999 127.0.0.1 8888
"""