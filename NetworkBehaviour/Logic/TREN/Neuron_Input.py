from NetworkBehaviour.Logic.TREN.Helper.Functions_Helper import *
from NetworkBehaviour.Input.Activator import *

class TREN_external_input(NeuronActivator):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.strength = self.get_init_attr('strength', 1.0, neurons)
        neurons.input = np.zeros(neurons.size)
        self.write_to = 'input'


    def new_iteration(self, neurons):
        neurons.input *= 0
        super().new_iteration(neurons)
        neurons.input *= self.strength


class InterGammaGlutamate(Behaviour):
    modificaton_reset_vars = ['']

    def set_variables(self, neurons):
        self.add_tag('Inter GLU')
        neurons.glu_inter_gamma_activity = neurons.get_neuron_vec()
        neurons.require_synapses('GLU')


    def new_iteration(self, neurons):
        neurons.glu_inter_gamma_activity *= 0

        for s in neurons.afferent_synapses['GLU']:
            s.slow_add=np.dot(s.W, s.src.output_activity_history[0])
            s.dst.glu_inter_gamma_activity+=s.slow_add
            #s.get_dest_vec('glu_inter_gamma_activity')[:] += np.dot(s.W, s.get_src_vec_obj(s.src.output_activity_history[0])[:])

    def get_shared_variable(self, name):
        if name == 'buffer_size':
            return 1



class IntraGammaGlutamate(Behaviour):
    def set_variables(self, neurons):
        self.add_tag('Intra GLU')
        neurons.glu_intra_gamma_activity = neurons.get_neuron_vec()

        neurons.require_synapses('GLU')


    def new_iteration(self, neurons):
        neurons.glu_intra_gamma_activity *= 0
        for s in neurons.afferent_synapses['GLU']:
            if hasattr(s.src, 'glu_inter_gamma_activity'):
                s.fast_add=np.dot(s.W,  relu3(s.src.glu_inter_gamma_activity, neurons.TH,  0))
                s.dst.glu_intra_gamma_activity += s.fast_add
                #s.get_dest_vec('glu_intra_gamma_activity')[:] += np.dot(s.W,  relu3(s.get_src_vec('glu_inter_gamma_activity')[:], neurons.TH,  0))


class IntraGammaGABA(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Intra GABA')
        self.GABA_density = self.get_init_attr('GABA_density', 1.0, neurons)
        self.GABA_random_factor = self.get_init_attr('GABA_random_factor', 0.0, neurons)
        self.GABA_Norm = self.get_init_attr('GABA_Norm', 4.3, neurons)

        all_neurons_same = self.get_init_attr('all_neurons_same', False, neurons)

        neurons.gaba_intra_gamma_activity = neurons.get_neuron_vec()

        neurons.require_synapses('GABA')

        self.initialize_synapse_attr('W', self.GABA_density, 1.0, self.GABA_random_factor, neurons, 'GABA', all_neurons_same)

        self.normalize_synapse_attr('W', 'W', self.GABA_Norm, neurons, 'GABA')




    def new_iteration(self, neurons):
        neurons.gaba_intra_gamma_activity *= 0
        for s in neurons.afferent_synapses['GABA']:
            s.dst.gaba_intra_gamma_activity -= np.dot(s.W, relu3(s.src.glu_inter_gamma_activity, neurons.TH, 0))
            #s.get_dest_vec('gaba_intra_gamma_activity')[:] -= np.dot(s.GABA_Synapses, relu3(s.get_src_vec('glu_inter_gamma_activity')[:],neurons.TH,0))


    def get_shared_variable(self, name):
        if name == 'buffer_size':
            return 1


class ActivityBuffering(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Collect and Buffer')
        #self.store_input = self.get_init_attr('store_input', True)
        self.min_buffersize = self.get_init_attr('min_buffersize', 2, neurons)
        self.activity_multiplyer = self.get_init_attr('activity_multiplyer', 0.0, neurons)
        neurons.TH = self.get_init_attr('firetreshold', 0.1, neurons)

        buffersize = np.max(neurons.get_shared_variables('buffer_size'))#problem:2 verschiedene gruppen

        neurons.activity = neurons.get_neuron_vec()
        neurons.output_activity_history = neurons.get_neuron_vec_buffer(buffersize)


    def new_iteration(self, neurons):

        neurons.activity *= self.activity_multiplyer
        neurons.activity += neurons.glu_inter_gamma_activity.copy()

        #experimetal...
        neurons.pre_inhibition_act = neurons.activity.copy()

        if hasattr(neurons, 'glu_intra_gamma_activity'):
            neurons.activity += neurons.glu_intra_gamma_activity
        if hasattr(neurons, 'gaba_intra_gamma_activity'):
            neurons.activity += neurons.gaba_intra_gamma_activity
        if hasattr(neurons, 'random_leak_activity'):
            neurons.activity += neurons.random_leak_activity


        neurons.activity = np.clip(neurons.activity, 0, 1)

        #if self.store_input:
        #    neurons.input_activity_history = roll(neurons.input_activity_history)#np.roll(neurons.input_activity_history, 1, axis=0)
        #    neurons.input_activity_history[0] = neurons.activity

        neurons.output_activity_history = roll(neurons.output_activity_history)#np.roll(neurons.output_activity_history, 1, axis=0)
        neurons.output = np.copy(relu3(neurons.activity+neurons.input, neurons.TH, 0.0))
        neurons.output_activity_history[0] = neurons.output#0.1#
        #neurons.output_activity_history[0] = np.copy(neurons.activity)

    def get_shared_variable(self, name):
        if name == 'buffer_size':
            return self.min_buffersize


class RandomLeakInput(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Random Leak')
        neurons.random_leak_activity = neurons.get_neuron_vec()
        self.random_strength = self.get_init_attr('random_strength', 1, neurons)

    def new_iteration(self, neurons):
        neurons.random_leak_activity = neurons.get_random_neuron_vec()*neurons.weight_norm_factor*self.random_strength

class additional(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('additional ...')
        neurons.output_new = neurons.get_neuron_vec()
        neurons.excitation = neurons.get_neuron_vec()
        neurons.inhibition = neurons.get_neuron_vec()
        neurons.input_act = neurons.get_neuron_vec()
        neurons.refractory_counter = neurons.get_neuron_vec()
        neurons.nox = neurons.get_neuron_vec()

        for s in neurons.afferent_synapses['GLU']+neurons.afferent_synapses['GABA']:
            s.slow_add = neurons.get_neuron_vec()
            s.fast_add = neurons.get_neuron_vec()


    def new_iteration(self, neurons):
        return

