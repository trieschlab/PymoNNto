import time
start_time=time.time()

from brian2 import *






defaultclock.dt = 0.1*ms


start_scope()

eqs = '''
dv/dt=(0*mV-v)/tau : volt
tau : second
'''

G = NeuronGroup(100, eqs, method='euler')
G.v = np.zeros(100)+1*mV
G.tau = 100*ms

M = StateMonitor(G, 'v', record=True)
print('t1', time.time()-start_time)

start_time=time.time()
run(100000*ms)
print('t2', time.time()-start_time)

for vrec in M.v:
    plot(M.t, vrec/mV)
show()













