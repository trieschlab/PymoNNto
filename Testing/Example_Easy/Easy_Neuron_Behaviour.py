from NetworkBehaviour.Basics.BasicNeuronBehaviour import *
#from NetworkCore.Neuron_Group import *
#from NetworkCore.Neuron_Behaviour import *
#from NetworkBehaviour.Basics.BasicNeuronBehaviour import *
#from NetworkBehaviour.Input.Activator import *
#import scipy.sparse as sp
#import matplotlib.pyplot as plt


class Easy_neuron_initialize(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Easy_neuron_initialize')

        #create neuron group variables
        neurons.activation = neurons.get_neuron_vec()
        neurons.output = neurons.get_neuron_vec()
        # equivalent to: np.zeros(neurons.size)

        #create random synapse weights
        for synapse_group in neurons.afferent_synapses['GLUTAMATE']:
            synapse_group.W = synapse_group.get_random_synapse_mat()*0.0001
            #synapse_group.get_synapse_mat() #equivalent to np.zeros(s.get_synapse_mat_dim())

    def new_iteration(self, neurons):
        neurons.activation *= 0.0


class Easy_neuron_collect_input(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Easy_neuron_collect_input')

    def new_iteration(self, neurons):
        for s in neurons.afferent_synapses['GLUTAMATE']:
            neurons.activation += s.W.dot(s.src.output)

        neurons.activation += neurons.get_random_neuron_vec(density=0.1)


class Easy_neuron_generate_output(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Easy_neuron_generate_output')
        neurons.TH = self.get_init_attr('threshold', 0.5, neurons)

    def new_iteration(self, neurons):
        neurons.output = (neurons.activation > neurons.TH).astype(np.float64)
