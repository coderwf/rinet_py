
# -*- coding:utf-8 -*-

import log
from ioloop import IoLoop
import pipe
import socket
import errno

#-----------------------------------------------------
def Join_host_port(host,port) :
    return str(host) + ":" + str(port)


def Listen(bind_host,bind_port,host,port,backlog=5):
    return Listener(bind_host,bind_port,host,port,backlog)


def Connect(host,port,retries=3):
    sock  = socket.socket()
    for i in range(0,retries) :
        try :
            sock.connect((host, port))
            return sock
        except :
            pass
    return None

class Listener(log.Logger):
    def __init__(self,bind_host,bind_port,host,port,backlog=5):
        log.Logger.__init__(self,"Listener@"+Join_host_port(bind_host,bind_port))
        self.set_level(log.DEBUG)
        self.host         = host
        self.port         = port
        self._loop  = IoLoop.instance()
        self.listen_sock  = socket.socket()
        self.listen_sock.setblocking(False)
        self.listen_sock.bind((bind_host,bind_port))
        self.listen_sock.listen(backlog)
        self.bind_host    = bind_host
        self.bind_port    = bind_port
        self._closed      = False

    ###接收连接
    def handle_accept(self,fd,events):
        ####一次最多处理5个连接
        for i in range(0,5) :
            try :
                _from , addr = self.listen_sock.accept()
                self.Info("New connection from %s",addr)
                _to          = Connect(self.host,self.port,2)

                if _to == None :
                    self.Warning("Can't connect to %s",Join_host_port(self.host,self.port))
                    _from.close()
                else :
                    pipe_ , err = pipe.Join(_from,_to)
                    if err != None :
                        self.Warning("Can't create pipe at exception %s",err)
                        _from.close()
                    else :
                        self.Info("Pipe %s created,Join %s with %s",pipe_._id,_from.getsockname(),_to.getsockname())
            except socket.error, e:
                if e[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                    continue
                else:
                    self.close()

    def start_listen(self):
        self._loop.add_handler(self.listen_sock,self.handle_accept,IoLoop.READ)
        self.Info("Start listen @" + Join_host_port(self.bind_host,self.bind_port))

    def close(self):
        if self._closed :
            return
        self.closed = True
        self._loop.remove_handler(self.listen_sock)
        self.listen_sock.close()
        self.listen_sock  = None
        self.Info("Listener closed.")


if __name__ == "__main__" :
    pass

