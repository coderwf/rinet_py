
# -*- coding:utf-8 -*-

###测试转发是否成功

import socket
import threading

def echo(sock) :
    ##sock = socket.socket()
    while True :
        chunk = sock.recv(1024*1024)
        sock.send(chunk)

class EchoT(threading.Thread) :
    def __init__(self,sock):
        threading.Thread.__init__(self)
        self.sock  = sock

    def run(self):
        try :
            echo(self.sock)
        except Exception , e:
            print e
        finally:
            self.sock.close()

if __name__ == "__main__":
    sock = socket.socket()
    sock.bind(("127.0.0.1",8888))
    sock.listen(5)
    while True :
        cli , addr = sock.accept()
        EchoT(cli).start()