import sys
sys.path.append('../../')
from NetworkCore.Network import *
from NetworkCore.Synapse_Group import *
from NetworkCore.Neuron_Group import *
from NetworkBehaviour.Logic.EulerEquationModules.EulerClock import *
from NetworkBehaviour.Logic.EulerEquationModules.VariableInitializer import *
from NetworkBehaviour.Logic.EulerEquationModules.Equation import *
from matplotlib.pyplot import *
from Exploration.Network_UI.Network_UI import *
from NetworkBehaviour.Structure.Structure import *











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






















