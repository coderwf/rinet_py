# -*- coding:utf-8 -*-

import random
csprng = random.SystemRandom()

MAX_INT_32  = (1 << 31) - 1

##产生一个随机的id
def rand_id(idlen):
    id  = ""
    randint = random.randint(0,MAX_INT_32)
    for i in range(idlen) :
        id += "{:x}".format(randint & 0xf)
        randint = randint >> 8
        ##产生一个新的随机数
        if i % 4 == 0 :
            randint = random.randint(0, MAX_INT_32)
    return id

##产生安全的随机id
def secure_rand_id(idlen):
    id = ""
    randint = csprng.randint(0, MAX_INT_32)
    for i in range(idlen):
        id += "{:x}".format(randint & 0xf)
        randint = randint >> 8
        ##产生一个新的随机数
        if i % 4 == 0:
            randint = csprng.randint(0, MAX_INT_32)
    return id

##产生一个随机的种子
def seed() :
    return random.randint(0,MAX_INT_32)

##产生一个安全的随机种子
def secure_seed() :
    return csprng.randint(0,MAX_INT_32)

##
if __name__ == "__main__":
    print seed()
    print secure_seed()
    print rand_id(10)
    print secure_rand_id(10)