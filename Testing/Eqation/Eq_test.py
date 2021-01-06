import sys
sys.path.append('../../')
from SORNSim.NetworkCore.Network import *
from SORNSim.NetworkCore.Synapse_Group import *
from SORNSim.NetworkCore.Neuron_Group import *
from SORNSim.NetworkBehaviour.Logic.EulerEquationModules.EulerClock import *
from SORNSim.NetworkBehaviour.Logic.EulerEquationModules.VariableInitializer import *
from SORNSim.NetworkBehaviour.Logic.EulerEquationModules.Equation import *
from matplotlib.pyplot import *
from SORNSim.Exploration.Network_UI.Network_UI import *
from SORNSim.NetworkBehaviour.Structure.Structure import *
import time










net = Network()

ng = NeuronGroup(net=net, size=100, behaviour={
    1: ClockModule(step='0.1*ms'),
    2: Variable(eq='v=1*mV'),
    3: Variable(eq='tau=100*ms'),
    4: EquationModule(eq='dv/dt=(0*mV-v)/tau'),

    100: Recorder(['n.v', 'n.t'], tag='my_rec')
})

net.initialize(info=False)

t=time.time()
net.simulate_iterations('10000*ms')
print(time.time()-t)

plot(net['n.t', 0], net['n.v', 0])
show()






















