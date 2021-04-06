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
