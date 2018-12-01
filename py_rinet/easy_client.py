
# -*- coding:utf-8 -*-

import socket
import random
import time
##测试转发效果

s   = "qwertyuioplkjhmgnvbfdcsxza"
sl  = len(s)

def genRandomStr(num) :
    res_str = ""
    for i in range(0,num) :
        res_str += s[random.randint(0,sl-1)]
    return res_str

if __name__ == "__main__":
    cli  = socket.socket()
    cli.connect(("127.0.0.1",9999))
    while True :
        res_str = genRandomStr(random.randint(20,50))
        print "send>>",res_str
        cli.send(res_str)
        chunk = cli.recv(1024*1024)
        print "resv>>",chunk
        time.sleep(random.uniform(0.1,1))
