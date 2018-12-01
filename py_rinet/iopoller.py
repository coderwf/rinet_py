
# -*- coding:utf-8 -*-

"""
将文件描述符注册到epoll中,当某个文件有io事件发生时,可以通过epoll
获取所有事件及相应的描述符,从而实现io多路复用,提高io的效率.
"""

import log
import select
UseSelect   = False

#----------描述事件----------------------------
_EPOLLIN = 0x001
_EPOLLPRI = 0x002
_EPOLLOUT = 0x004
_EPOLLERR = 0x008
_EPOLLHUP = 0x010
_EPOLLRDHUP = 0x2000
_EPOLLONESHOT = (1 << 30)
_EPOLLET = (1 << 31)
#----------------------------------------------
##epoll中需要用到的io事件
NONE = 0
READ = _EPOLLIN
WRITE = _EPOLLOUT
ERROR = _EPOLLERR | _EPOLLHUP | _EPOLLRDHUP

#

class _KQueue(object):
    """BSD/Mac系统"""
    def __init__(self):
        self._kqueue = select.kqueue()
        self._active = {}

    def fileno(self):
        return self._kqueue.fileno()

    def register(self, fd, events):
        self._control(fd, events, select.KQ_EV_ADD)
        self._active[fd] = events

    def modify(self, fd, events):
        self.unregister(fd)
        self.register(fd, events)

    def unregister(self, fd):
        events = self._active.pop(fd)
        self._control(fd, events, select.KQ_EV_DELETE)

    def _control(self, fd, events, flags):
        kevents = []
        if events & READ:
            kevents.append(select.kevent(
                    fd, filter=select.KQ_FILTER_WRITE, flags=flags))
        if events & READ or not kevents:
            # Always read when there is not a write
            kevents.append(select.kevent(
                    fd, filter=select.KQ_FILTER_READ, flags=flags))
        # Even though control() takes a list, it seems to return EINVAL
        # on Mac OS X (10.6) when there is more than one event in the list.
        for kevent in kevents:
            self._kqueue.control([kevent], 0)

    def poll(self, timeout):
        kevents = self._kqueue.control(None, 1000, timeout)
        events = {}
        for kevent in kevents:
            fd = kevent.ident
            flags = 0
            if kevent.filter == select.KQ_FILTER_READ:
                events[fd] = events.get(fd, 0) | READ
            if kevent.filter == select.KQ_FILTER_WRITE:
                events[fd] = events.get(fd, 0) | WRITE
            if kevent.flags & select.KQ_EV_ERROR:
                events[fd] = events.get(fd, 0) | ERROR
        return events.items()


class _Select(object):
    """基于非linux系统中最简单的select"""
    def __init__(self):
        self.read_fds  = set()
        self.write_fds = set()
        self.error_fds = set()
        self.fd_sets = (self.read_fds, self.write_fds, self.error_fds)

    def register(self, fd, events):
        if events & READ:  self.read_fds.add(fd)
        if events & WRITE: self.write_fds.add(fd)
        if events & ERROR: self.error_fds.add(fd)

    def modify(self, fd, events):
        self.unregister(fd)
        self.register(fd, events)

    def unregister(self, fd):
        self.read_fds.discard(fd)
        self.write_fds.discard(fd)
        self.error_fds.discard(fd)

    def poll(self, timeout):
        readable, writeable, errors = select.select(
            self.read_fds, self.write_fds, self.error_fds, timeout)
        events = {}
        for fd in readable:
            events[fd] = events.get(fd, 0) | READ
        for fd in writeable:
            events[fd] = events.get(fd, 0) | WRITE
        for fd in errors:
            events[fd] = events.get(fd, 0) | ERROR
        return events.items()

class _EPoll(object):
    """An epoll-based event loop using our C module for Python 2.5 systems"""
    _EPOLL_CTL_ADD = 1
    _EPOLL_CTL_DEL = 2
    _EPOLL_CTL_MOD = 3

    def __init__(self):
        self._epoll_fd = epoll.epoll_create()

    def fileno(self):
        return self._epoll_fd

    def register(self, fd, events):
        epoll.epoll_ctl(self._epoll_fd, self._EPOLL_CTL_ADD, fd, events)

    def modify(self, fd, events):
        epoll.epoll_ctl(self._epoll_fd, self._EPOLL_CTL_MOD, fd, events)

    def unregister(self, fd):
        epoll.epoll_ctl(self._epoll_fd, self._EPOLL_CTL_DEL, fd, 0)

    def poll(self, timeout):
        return epoll.epoll_wait(self._epoll_fd, int(timeout * 1000))


"""如果是linux系统则优先使用epoll,否则使用kqueue,如果都没有则使用最简单的select"""
if hasattr(select, "epoll"):
    _poll = select.epoll
elif hasattr(select, "kqueue"):
    _poll = _KQueue
else:
    try:
        import epoll
        _poll = _EPoll
    except:
        UseSelect = True
        _poll = _Select


class IoPoller(log.Logger):
    def __init__(self,level=log.DEBUG):
        log.Logger.__init__(self,"IOPOLLER",time_prefix=True,level=level)
        self.poller = _poll()
        if UseSelect :
            self.Info("Fall back to use select.")

    def register(self, fd, events):
        self.Info("Register fd %s",fd)
        self.poller.register(fd,events)

    def modify(self, fd, events):
        self.Info("Modify fd %s", fd)
        self.poller.modify(fd,events)

    def unregister(self, fd):
        self.Info("Unregister fd %s",fd)
        self.poller.unregister(fd)

    ###默认10ms
    def poll(self, timeout=0.1):
        self.Debug("Poll after %s s",timeout)
        return self.poller.poll(timeout)

if __name__ == "__main__":
    io_poller = IoPoller()
    io_poller.register(12,READ)
    io_poller.unregister(12)
