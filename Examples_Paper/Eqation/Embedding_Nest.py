from PymoNNto import *
import nest

class Nest_embedding(Behaviour):

    def set_variables(self, neurons):
        # define resolution
        nest.SetKernelStatus({'resolution':1.0})

        # define neuron model
        self.G = nest.Create(
            "iaf_psc_delta", 1, params={
                'E_L': 1.0,
                't_ref': 1.0,
                'V_th': 0.9,
                'V_reset': 0.}
            )


        # set variables
        nest.SetStatus(self.G, 'V_m', 0.0)
        nest.SetStatus(self.G, 'tau_m', 100.0)

    def new_iteration(self, n):
        nest.Simulate(1.0)
        n.v = nest.GetStatus(self.G, 'V_m')


My_Network = Network()

My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=get_squared_dim(1), behaviour={
    1: Nest_embedding()
})

My_Network.initialize()

from PymoNNto.Exploration.Network_UI import *
my_UI_modules = get_default_UI_modules(['v'], ['W'])
Network_UI(My_Network, modules=my_UI_modules, label='My_Network_UI', group_display_count=1).show()