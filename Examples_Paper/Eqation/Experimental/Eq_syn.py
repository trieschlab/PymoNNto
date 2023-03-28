import sys
sys.path.append('../../')
from PymoNNto.NetworkCore.Network import *
from PymoNNto.NetworkCore.Synapse_Group import *
from NetworkBehavior.EulerEquationModules.Equation import *
from matplotlib.pyplot import *
from PymoNNto.NetworkBehavior.Structure.Structure import *

from Examples_Paper.Eqation.Experimental.event_based_processing import *


class my_beh1(Behavior):

    def initialize(self, syn):
        print('set1')
        return

    def iteration(self, syn):
        print('iteration1')
        return

class my_beh2(Behavior):

    def initialize(self, syn):
        print('set2')
        return

    def iteration(self, syn):
        print('iteration2')
        return


class my_beh3(Behavior):

    def initialize(self, syn):
        print('set3')
        return

    def iteration(self, syn):
        print('iteration3')
        return


net = Network(behavior={})#6: my_beh1(tag='tag1')

ng = NeuronGroup(net=net, size=100, behavior={
    1: ClockModule(step='10*ms'),
    2: Variable(eq='v=n.vector("uniform")*0.1*mV'),
    3: Variable(eq='tau=10*ms+n.vector("uniform")*200*ms'),
    5: EquationModule(eq='dv/dt=(0*mV-v)/tau'),

    7: neuron_event(condition='n.v<0.01', eq='n.v_new=1'),

    #7: my_beh2(tag='tag2'),

    100: Recorder(['v', 't'], tag='my_rec')
})

syn = SynapseGroup(net=net, src=ng, dst=ng, behavior={
    2: Syn_Variable(eq='w=s.matrix("uniform")*0.01'),
    6: on_pre(src_condition='src.v>0.9', eq='dst.v_new+=s.w;src.v_new=0.1')
})#my_beh3(tag='tag3') #8: on_pre(src_condition='src.v<0.01', eq='src.v_new=1')

net.initialize(info=False)

net.simulate_iterations('1000*ms')

plot(net['t', 0], net['v', 0])
show()






















