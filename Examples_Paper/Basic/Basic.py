from PymoNNto import *

class Basic_Behavior(Behavior):

    def initialize(self, neurons):
        neurons.voltage = neurons.vector()
        self.threshold = 0.5
        self.leak_factor = self.parameter('leak_factor', 0.9, neurons)

    def iteration(self, neurons):
        neurons.spike = neurons.voltage > self.threshold #spikes
        neurons.voltage[neurons.spike] = 0.0 #reset

        neurons.voltage *= self.leak_factor #voltage decay
        neurons.voltage += neurons.vector('uniform',density=0.01) #noise

class Input_Behavior(Behavior):

    def initialize(self, neurons):
        for synapse in neurons.synapses(afferent, 'GLUTAMATE'):
            synapse.W = synapse.matrix('uniform', density=0.1)
            synapse.enabled = synapse.W > 0

    def iteration(self, neurons):
        for synapse in neurons.synapses(afferent, 'GLUTAMATE'):
            neurons.voltage += synapse.W.dot(synapse.src.spike)/synapse.src.size*10



My_Network = Network()

My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=get_squared_dim(100), behavior={
    1: Basic_Behavior(),
    2: Input_Behavior(),
    #9: Recorder(['voltage', 'np.mean(voltage)'], tag='my_recorder'),
    #10: EventRecorder('spike', tag='my_event_recorder')
})

#My_Neurons.visualize_module()

my_syn = SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE')

My_Network.initialize()

#my_syn.enabeled = my_syn.W > 0

#My_Network.simulate_iterations(200, measure_block_time=True)

#import matplotlib.pyplot as plt
#plt.plot(My_Network['voltage', 0, 'np'][:, 0:10])
#plt.plot(My_Network['np.mean(voltage)', 0], color='black')
#plt.axhline(My_Neurons['Basic_Behavior', 0].threshold, linestyle='dashed')
#plt.xlabel('iterations (ms)')
#plt.ylabel('voltage')
#plt.show()

#plt.plot(My_Network['spike.t', 0], My_Network['spike.i', 0], '.k')
#plt.xlabel('iterations (ms)')
#plt.ylabel('neuron index')
#plt.show()

from PymoNNto.Exploration.Network_UI import *
from Examples_Paper.Basic.Basic_Tab import *
my_UI_modules = [MyUITab()] + get_default_UI_modules(['voltage', 'spike'], ['W'])
Network_UI(My_Network, modules=my_UI_modules, label='My_Network_UI', group_display_count=1).show()
