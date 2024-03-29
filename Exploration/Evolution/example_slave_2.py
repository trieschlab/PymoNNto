from PymoNNto import *
from PymoNNto.Exploration.Evolution.Interface_Functions import *
import numpy as np
import matplotlib.pyplot as plt

class Counter(Behavior):
    def initialize(self, neurons):
        self.inc = self.parameter('inc', 1.0)
        neurons.count = np.zeros(neurons.size)#neurons.vector()
        plt.plot([1,2,3])
        plt.show()

    def iteration(self, neurons):
        neurons.count += self.inc


My_Network = Network()
My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=100, behavior={
    1: Counter(inc='[2.0#a]'),
    2: Recorder('count')
})
My_Synapses = SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE')
sm = StorageManager('test', random_nr=False, print_msg=False)
My_Network.initialize(storage_manager=sm)

My_Network.simulate_iterations(100)

score = np.mean(My_Neurons.count)

set_score(score)

