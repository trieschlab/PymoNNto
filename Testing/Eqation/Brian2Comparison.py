from brian2 import *
#%matplotlib inline












start_scope()

eqs = '''
dv/dt=(0*mV-v)/tau : volt
tau : second
'''

G = NeuronGroup(100, eqs, method='euler')
G.v = np.zeros(100)+1*mV
G.tau = 100*ms

M = StateMonitor(G, 'v', record=True)

run(1000*ms)

for vrec in M.v:
    plot(M.t, vrec/mV)
show()












