
# -*- coding:utf-8 -*-

"""循环事件模型,不断获取io事件,并执行事件对应的handle"""

import log
import threading
import bisect
import time
import iopoller
log.RootLogger.set_level(log.INFO)
_EPOLLIN = 0x001
_EPOLLPRI = 0x002
_EPOLLOUT = 0x004
_EPOLLERR = 0x008
_EPOLLHUP = 0x010
_EPOLLRDHUP = 0x2000
_EPOLLONESHOT = (1 << 30)
_EPOLLET = (1 << 31)


#--------------------------------------------------------------
class IoLoop(log.Logger):
    instance_lock  = threading.Lock() ###单例模式双重检查锁
    NONE = 0
    READ = _EPOLLIN
    WRITE = _EPOLLOUT
    ERROR = _EPOLLERR | _EPOLLHUP | _EPOLLRDHUP
    def __init__(self,level=log.DEBUG):
        log.Logger.__init__(self,"IOLOOP",level=level)
        self._callbacks   = list()
        self._timeouts    = list()
        self._handlers    = dict()
        self._events      = dict()
        self._running     = False
        self._stopped     = True
        self._impl        = iopoller.IoPoller(level=log.INFO)
    ###单例模式,使用双重检查锁
    @classmethod
    def instance(cls,level=log.DEBUG):
        if hasattr(cls,"_instance_"):
            return cls._instance_
        ##try finally
        try :
            IoLoop.instance_lock.acquire()
            if not hasattr(cls, "_instance_"):
                cls._instance_ = IoLoop(level=level)
                log.RootLogger.Info("Ioloop instance created")
            return cls._instance_
        finally:
            IoLoop.instance_lock.release()

    def running(self):
        return self._running

    def stop(self):
        if self._stopped :
            return
        self.Info("IoLoop Stop")
        self._running  = False
        self._stopped  = True

    def start(self):
        if self._stopped :
            self._stopped = False
        self._running = True
        self.Info("Ioloop start")
        while not self._stopped :
            """run callbacks"""
            poll_timeout  = 0.2 ##//TODO:这个时间需要根据timeout事件的时间重新计算
            while self._callbacks:
                if self._stopped:  ###ioloop可能会被停止
                    return
                callback = self._callbacks.pop(0)  ##fifo
                self._run_callback_(callback)

            """run timeouts"""
            while self._timeouts:
                if self._stopped:  ###ioloop可能会被停止
                    return
                now = int(time.time() * 1000)
                if self._timeouts[0].deadline > now:
                    break
                timeout = self._timeouts.pop(0)
                self._run_callback_(timeout.callback)
            """io event"""
            try :
                event_pairs = self._impl.poll(poll_timeout)
            except Exception , e :
                ##self.Error("Exception %s in poll io events",e)
                continue
            self._events.update(event_pairs)
            while self._events :
                fd , events = self._events.popitem()
                handle      = self._handlers.get(fd,None)
                if handle == None :
                    self.Warning("fd %d handler is None",fd)
                    continue
                self._run_callback_(handle,fd,events)

    def _run_callback_(self,callback,*args,**kwargs):
        try :
            callback(*args,**kwargs)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception , e :
            self.handle_callback_exception(e,callback)

    def handle_callback_exception(self,e,callback):
        self.Error("Exception %s in callback %r",e,callback)

    def add_callback(self,callback):
        self._callbacks.append(callback)
        return callback

    def remove_callback(self,callback):
        self._callbacks.remove(callback)

    def add_deadline(self,deadline,callback):
        self.Info("Add deadline")
        timeout = _Timeout(deadline,callback)
        bisect.insort(self._timeouts,timeout)
        return timeout

    def remove_timeout(self,timeout):
        self._timeouts.remove(timeout)

    def add_timeout(self,timeout,callback):
        deadline  = int(time.time() *1000) + timeout
        return self.add_deadline(deadline,callback)

    def split_fd(self,fd):
        try :
            return fd.fileno() , fd
        except :
            self.Warning("Can't split fd %r",fd)
            return fd, fd

    def add_handler(self, fd, handler, events):
        """添加一个文件描述符io监听"""
        fd , _ = self.split_fd(fd)
        self.Info("Add fd %s , handler %r", fd, handler.func_name)
        self._handlers[fd] = handler
        self._impl.register(fd, events | iopoller.ERROR)

    def update_handler(self, fd, events):
        fd, _ = self.split_fd(fd)
        self.Info("Update fd %s events", fd)
        self._impl.modify(fd, events | iopoller.ERROR)

    def remove_handler(self, fd):
        fd , _ = self.split_fd(fd)
        self.Info("Remove fd %s", fd)
        self._handlers.pop(fd, None)
        self._events.pop(fd, None)
        try:
            self._impl.unregister(fd)
        except (OSError, IOError):
            self.Error("Error deleting fd %d from IOLoop", fd,exc_info=True)

"""定时事件"""
class _Timeout(object):
    """减少内存使用空间"""
    __slots__ = ["deadline", "callback"]

    def __init__(self, deadline, callback):
        self.deadline = deadline
        self.callback = callback

    def __cmp__(self, other):
        return cmp((self.deadline, id(self.callback)),
                   (other.deadline, id(other.callback)))


"""周期性定时任务
   周期事件单位为ms
"""
class PeriodicCallback(object):
    def __init__(self, callback, callback_time):
        self.callback       = callback
        self.callback_time  = callback_time
        self.io_loop        = IoLoop.instance()
        self._running       = True

    ###用run包装callback并放入ioloop中
    def start(self):
        deadline = int(time.time()*1000) + self.callback_time
        self.io_loop.add_deadline(deadline, self._run)

    def stop(self):
        self._running = False

    def _run(self):
        ##如果停止则直接返回
        if not self._running: return
        self.callback()
        ###执行完了以后如果没停止则继续放入ioloop循环中
        if self._running :
            self.start()

def print_hello():
    print "hello"

if __name__ == "__main__":
    pc = PeriodicCallback(print_hello,2000)
    pc.start()
    IoLoop.instance().add_timeout(2000,None)
    IoLoop.instance().start()



