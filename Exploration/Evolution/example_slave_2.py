from PymoNNto import *
from PymoNNto.Exploration.Evolution.Interface_Functions import *
import numpy as np
import matplotlib.pyplot as plt

class Counter(Behaviour):
    def set_variables(self, neurons):
        self.inc = self.get_init_attr('inc', 1.0)
        neurons.count = np.zeros(neurons.size)#neurons.get_neuron_vec()
        plt.plot([1,2,3])
        plt.show()

    def new_iteration(self, neurons):
        neurons.count += self.inc


My_Network = Network()
My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=100, behaviour={
    1: Counter(inc='[2.0#a]'),
    2: Recorder(variables=['n.count'])
})
My_Synapses = SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE')
sm = StorageManager('test', random_nr=False, print_msg=False)
My_Network.initialize(storage_manager=sm)

My_Network.simulate_iterations(100)

score = np.mean(My_Neurons.count)

set_score(score)

