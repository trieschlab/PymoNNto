import time
import numpy as np

a=np.zeros(10000)

start=time.time()
cmd='a'
for i in range(100000):
    x=eval(cmd)
print(time.time()-start)

start=time.time()
cmd=compile('a', '<string>', 'eval')
for i in range(100000):
    x=eval(cmd)
print(time.time()-start)

start=time.time()
for i in range(100000):
    x=a
print(time.time()-start)

def do():
    x=a
start=time.time()
for i in range(100000):
    do()
print(time.time()-start)