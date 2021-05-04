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






















