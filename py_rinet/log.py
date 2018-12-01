
# -*- coding:utf-8 -*-

import logging
logging.basicConfig(level=logging.DEBUG)
import time

#--------------import----------------------------------------------

class Logger(object):
    def __init__(self,name,time_prefix=True,level=logging.DEBUG):
        self.name        = name
        self.logger      = logging.getLogger(self.name)
        self.logger.setLevel(level=level)
        self.time_prefix = time_prefix
        self.prefixes  = ""

    def add_prefix(self,prefix):
        self.prefixes  += "["+prefix+"]"

    def clear_prefixes(self):
        self.prefixes  = ""

    def Debug(self,msg,*args,**kwargs):
        self.logger.debug(self.prefix(msg),*args,**kwargs)

    def Info(self,msg,*args,**kwargs):
        self.logger.info(self.prefix(msg),*args,**kwargs)

    def Warning(self,msg,*args,**kwargs):
        self.logger.warning(self.prefix(msg),*args,**kwargs)

    def Error(self,msg,*args,**kwargs):
        self.logger.error(self.prefix(msg),*args,**kwargs)

    def Critical(self,msg,*args,**kwargs):
        self.logger.critical(self.prefix(msg),*args,**kwargs)

    def Warn(self,msg,*args,**kwargs):
        self.logger.warn(self.prefix(msg), *args,**kwargs)

    def set_level(self,level):
        self.logger.setLevel(level=level)

    def reset_level(self):
        self.logger.setLevel(level=logging.DEBUG)

    def prefix(self,msg):
        prefix = ""
        if self.time_prefix :
            prefix += self.add_time_prefix()
        prefix += self.prefixes
        sep = "" if prefix == "" else ":"
        return prefix + sep +msg

    def add_time_prefix(self):
        return "[" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +"]"

    def set_time_prefix(self):
        self.time_prefix = True

    def clear_time_prefix(self):
        self.time_prefix = False

DEBUG     = logging.DEBUG
WARN      = logging.WARN
WARNING   = logging.WARNING
ERROR     = logging.ERROR
INFO      = logging.INFO
CRATICAl  = logging.CRITICAL


RootLogger  = Logger("ROOT",level=logging.WARNING)


if __name__ == "__main__":
    pass




