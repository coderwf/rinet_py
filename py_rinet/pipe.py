# -*- coding:utf-8 -*-

import socket
import log
from ioloop import IoLoop
import util
import errno
#----------------------------------------------------

###生成一个双向传输的管道
def Join(_from,_to) :
    try :
        pipe = Pipe(_from, _to)
        pipe.register()
        return pipe , None
    except Exception , e :
        return None , e

class Pipe(log.Logger) :
    def __init__(self,_from,_to):
        log.Logger.__init__(self,"Pipe",level=log.INFO)
        self._id          = util.secure_rand_id(8)
        self._loop        = IoLoop.instance()
        self.add_prefix(self._id)
        self._from_buf    = ""
        self._to_buf      = ""
        self._from        = _from
        self._to          = _to
        self._from.setblocking(False)
        self._to.setblocking(False)
        self._from_bytes  = 0
        self._to_bytes    = 0
        self._read_chunk_size = 1024 * 1024 * 2
        self._closed      = False

    def close(self):
        if self._closed :
            return
        self._closed = True
        self._loop.remove_handler(self._from)
        self._loop.remove_handler(self._to)
        self._from.close()
        self.Info("Copied %s bytes from before closed",self._from_bytes)
        self._to.close()
        self.Info("Copied %s bytes to before closed",self._to_bytes)
        self._from  = None
        self._to    = None
        self.Info("Pipe %s closed",self._id)

    def handle_from(self,fd,events):
        if not self._from:
            self.Warning("socket %s closed", self._from)
            return
        if events & IoLoop.READ:
            err , chunk = self.read(self._from)
            if err == None :
                self._from_buf += chunk
                self._from_bytes += len(chunk)
        if not self._from:
            return
        if events & self._loop.WRITE:
            buffer = self._to_buf
            self._to_buf  = ""
            err , rest = self.write(self._from,buffer)
            if err == None :
                self._to_buf = rest + self._to_buf
        if not self._from:
            return
        if events & self._loop.ERROR:
            self.close()
            return

    def handle_to(self,fd,events):
        if not self._to:
            self.Warning("socket %s closed", self._to)
            return
        if events & IoLoop.READ:
            err , chunk = self.read(self._to)
            if err == None :
                self._to_buf += chunk
                self._to_bytes += len(chunk)
        if not self._to:
            return
        if events & self._loop.WRITE:
            buffer = self._from_buf
            self._from_buf  = ""
            err , rest = self.write(self._to,buffer)
            if err == None :
                self._from_buf = rest + self._from_buf
        if not self._to:
            return
        if events & self._loop.ERROR:
            self.close()
            return

    def read(self,sock):
        try:
            chunk = sock.recv(self._read_chunk_size)
        except socket.error, e:
            if e[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                return e , ""
            else:
                self.Warning("Read error on %s: %s",sock, e)
                self.close()
                return e , ""
        if not chunk: ##error
            self.Warning("Read blank chunk from %s",sock)
            self.close()
            return "" , ""
        return None , chunk

    def write(self,sock,buffer):
        while buffer:
            try:
                num_bytes   = sock.send(buffer)
                buffer      = buffer[num_bytes:]
            except socket.error, e:
                if e[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                    break
                else:
                    self.Warning("Write error on %s: %s",sock, e)
                    self.close()
                    return e , buffer
        return None , buffer

    def register(self):
        self._loop.add_handler(self._from, self.handle_from,IoLoop.READ |IoLoop.WRITE)
        self._loop.add_handler(self._to, self.handle_to,IoLoop.READ |IoLoop.WRITE)
        self.Info("Pipe %s registered",self._id)


def hello(arg):
    print arg

from functools import partial
if __name__ == "__main__":
    fun1 = partial(hello,12)
    fun2 = partial(hello,34)
    fun1()
    fun2()
    print id(fun1)
    print id(fun2)