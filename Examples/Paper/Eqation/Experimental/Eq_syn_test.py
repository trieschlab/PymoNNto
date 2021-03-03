import sys
sys.path.append('../../')
from PymoNNto.NetworkCore.Network import *
from PymoNNto.NetworkCore.Synapse_Group import *
from PymoNNto.NetworkBehaviour.Logic.EulerEquationModules.EulerClock import *
from PymoNNto.NetworkBehaviour.Logic.EulerEquationModules.VariableInitializer import *
from PymoNNto.NetworkBehaviour.Logic.EulerEquationModules.Equation import *
from matplotlib.pyplot import *
from PymoNNto.NetworkBehaviour.Structure.Structure import *

from Examples.Paper.Eqation.Experimental.event_based_processing import *


class my_beh1(Behaviour):

    def set_variables(self, syn):
        print('set1')
        return

    def new_iteration(self, syn):
        print('iteration1')
        return

class my_beh2(Behaviour):

    def set_variables(self, syn):
        print('set2')
        return

    def new_iteration(self, syn):
        print('iteration2')
        return


class my_beh3(Behaviour):

    def set_variables(self, syn):
        print('set3')
        return

    def new_iteration(self, syn):
        print('iteration3')
        return


net = Network(behaviour={})#6: my_beh1(tag='tag1')

ng = NeuronGroup(net=net, size=100, behaviour={
    1: ClockModule(step='10*ms'),
    2: Variable(eq='v=n.get_random_neuron_vec()*0.1*mV'),
    3: Variable(eq='tau=10*ms+n.get_random_neuron_vec()*200*ms'),
    5: EquationModule(eq='dv/dt=(0*mV-v)/tau'),

    7: neuron_event(condition='n.v<0.01', eq='n.v_new=1'),

    #7: my_beh2(tag='tag2'),

    100: Recorder(['n.v', 'n.t'], tag='my_rec')
})

syn = SynapseGroup(net=net, src=ng, dst=ng, behaviour={
    2: Syn_Variable(eq='w=s.get_random_synapse_mat()*0.01'),
    6: on_pre(src_condition='src.v>0.9', eq='dst.v_new+=s.w;src.v_new=0.1')
})#my_beh3(tag='tag3') #8: on_pre(src_condition='src.v<0.01', eq='src.v_new=1')

net.initialize(info=False)

net.simulate_iterations('1000*ms')

plot(net['n.t', 0], net['n.v', 0])
show()






















