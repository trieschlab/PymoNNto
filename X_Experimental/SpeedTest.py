import time
import numpy as np

a=np.random.rand(10000)


start=time.time()
for i in range(1000):
    b = a.copy()
    b[b<0.5]=0.5
print(time.time()-start)

start=time.time()
for i in range(1000):
    b = a.copy()
    b=np.clip(b, None, 0.5)
print(time.time()-start)

'''
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
'''