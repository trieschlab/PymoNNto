import time as time_p
import sys
sys.path.append('../../')
start_time=time_p.time()
from PymoNNto import *
from matplotlib.pyplot import *
from NetworkBehavior.EulerEquationModules.VariableInitializer import *
from NetworkBehavior.EulerEquationModules.Equation import *
from NetworkBehavior.EulerEquationModules.EulerClock import *








net = Network()

ng = NeuronGroup(net=net, size=100, behavior={
    1: Clock(step='0.1*ms'),
    2: Variable(eq='v=1*mV'),
    3: Variable(eq='tau=100*ms'),
    4: Equation(eq='dv/dt=(0*mV-v)/tau'),

    9: Recorder(['v', 't'], tag='my_rec')
})

net.initialize()
print('t1', time_p.time()-start_time)

start_time=time_p.time()
net.simulate_iterations('1000*ms')
print('t2', time_p.time()-start_time)

plot(net['t', 0], net['v', 0])
show()






















