# Differential Equation Modules

PymoNNto can also use differential equation description of NeuronGroups similar to Brian2.
In the next codeblocks we see a PymoNNto implementation which uses the EulerClock, VariableInitializer and Equation module to create a neurongroup with decaying voltage.
The code produces equivalent output as the Brian2 code in the code block below.

Pymonnto:
```python
import time as time_p
import sys
sys.path.append('../../')
start_time=time_p.time()
from PymoNNto import *
from matplotlib.pyplot import *
from PymoNNto.NetworkBehaviour.Logic.EulerEquationModules.EulerClock import *
from PymoNNto.NetworkBehaviour.Logic.EulerEquationModules.VariableInitializer import *
from PymoNNto.NetworkBehaviour.Logic.EulerEquationModules.Equation import *

net = Network()

ng = NeuronGroup(net=net, size=100, behaviour={
    1: ClockModule(step='0.1*ms'),
    2: Variable(eq='v=1*mV'),
    3: Variable(eq='tau=100*ms'),
    4: EquationModule(eq='dv/dt=(0*mV-v)/tau'),

    100: Recorder(['n.v', 'n.t'], tag='my_rec')
})

net.initialize(info=False)
print('t1', time_p.time()-start_time)

start_time=time_p.time()
net.simulate_iterations('100000*ms')
print('t2', time_p.time()-start_time)

plot(net['n.t', 0], net['n.v', 0])
show()
```

Brian2:
```python
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
```

#PymoNNto Brian 2 hybrid

There is also an option to embedd Brian2 inside of PymoNNto whcih we can see below. The new_iteration block creates some kind of bridge between the simulators which can be used for reading and writing into the embedded NeuronGroup.

```python
import PymoNNto as pmnt
from brian2 import *
from PymoNNto.NetworkCore.Behaviour import *



class Brian2_embedding(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Brian2_embedding')
        defaultclock.dt = 1 * ms

        eqs = self.get_init_attr('eqs', '')

        self.G = NeuronGroup(100, eqs, method='euler')      #this is a Biran2 NeuronGroup!
        self.net = Network(self.G)                          #this is a Biran2 Network!

        self.G.v = (np.random.rand(100) + 1) * mV
        self.G.tau = 100 * ms


    def new_iteration(self, neurons):
        self.net.run(1*ms)
        neurons.v = self.G.v / volt



My_Network = pmnt.Network()

eqs = '''
dv/dt=(0*mV-v)/tau : volt
tau : second
'''

My_Neurons = pmnt.NeuronGroup(net=My_Network, tag='my_neurons', size=pmnt.get_squared_dim(100), behaviour={
    1: Brian2_embedding(eqs=eqs)
})

My_Network.initialize()

from PymoNNto.Exploration.Network_UI import *
my_UI_modules = get_default_UI_modules(['v'], ['W'])
Network_UI(My_Network, modules=my_UI_modules, label='My_Network_UI', group_display_count=1).show()
```