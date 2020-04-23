from NetworkCore.Neuron_Group import *
from NetworkCore.Neuron_Behaviour import *
from NetworkBehaviour.Input.Activator import *

class external_input(NeuronActivator):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.strength = self.get_init_attr('strength', 1.0, neurons)
        neurons.input = np.zeros(neurons.size)
        self.write_to = 'input'

    def new_iteration(self, neurons):
        super().new_iteration(neurons)
        if self.strength != 0:
            neurons.activity += neurons.input * self.strength
            neurons.input *= 0

class IP(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('IP')
        neurons.target = self.get_init_attr('strength', 0.03, neurons)

    def new_iteration(self, neurons):
        neurons.TH += (neurons.output-neurons.target)*0.001


class STDP(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('STDP')
        neurons.output_old = neurons.get_neuron_vec()
        neurons.eta_stdp = self.get_init_attr('eta_stdp', 0.005, neurons)

    def new_iteration(self, neurons):
        for s in neurons.afferent_synapses['GLUTAMATE']:
            grow = s.dst.output[:, None] * s.src.output_old[None, :]
            shrink = s.dst.output_old[:, None] * s.src.output[None, :]

            dw = neurons.eta_stdp * (grow - shrink)

            s.W += dw * s.enabled
            s.W[s.W < 0.0] = 0.0

        neurons.output_old = neurons.output.copy()

        self.normalize_synapse_attr('W', 'W', neurons.syn_norm, neurons, 'GLUTAMATE')
