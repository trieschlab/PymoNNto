```python
from SORNSim import *
#SORNSim
net = Network()

ng = NeuronGroup(net=net, size=100, behaviour={
    1: ClockModule(step='100*ms'),
    2: Variable(eq='v=1*mV'),
    3: Variable(eq='tau=100*ms'),
    4: EquationModule(eq='dv/dt=(0*mV-v)/tau'),

    100: NeuronRecorder(['n.v', 'n.t'], tag='my_rec')
})

net.initialize(info=False)

net.simulate_iterations('1000*ms')

plot(net['n.t', 0], net['n.v', 0])
show()
```

```python
#Brian2
from brian2 import *
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
```