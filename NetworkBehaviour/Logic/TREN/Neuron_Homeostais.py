from NetworkBehaviour.Logic.Basics.BasicHomeostasis import *
from NetworkBehaviour.Logic.Basics.Normalization import *

class HomeostaticMechanism(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Homeostasis')
        self.ACTIVITY_COUNT_TH_MIN = self.get_init_attr('ACTIVITY_COUNT_TH_MIN', 0.0, neurons)#step height #neurons.firetreshold
        self.ACTIVITY_COUNT_TH_MAX = self.get_init_attr('ACTIVITY_COUNT_TH_MAX', 1.0, neurons)

        self.pattern_chance = self.get_init_attr('pattern_chance', 0.01, neurons)
        self.min = self.get_init_attr('min', self.pattern_chance, neurons)#*self.ACTIVITY_COUNT_TH_MIN
        self.max = self.get_init_attr('max', self.pattern_chance, neurons)#*self.ACTIVITY_COUNT_TH_MAX
        self.range_end = self.get_init_attr('range_end', 1000, neurons)
        self.inc = self.get_init_attr('inc', 0.01, neurons)
        self.dec = self.get_init_attr('dec', 0.01, neurons)

        self.target_min = self.get_init_attr('target_min', 0.1, neurons)#0.01
        self.target_max = self.get_init_attr('target_max', 100, neurons)#100000

        self.target_attr = self.get_init_attr('target_attr', 'weight_norm_factor', neurons)
        self.src_attr = self.get_init_attr('src_attr', 'output_activity_history[0]', neurons)

        self.avg = neurons.get_random_neuron_vec()*(self.max-self.min)+self.min

    def new_iteration(self, neurons):
        if neurons.learning:
            current_value = neurons.output_activity_history[0].copy()
            #current_value = getattr(neurons, self.src_attr).copy()#neurons.output_activity_history[0].copy() #input_activity_history  #COPY!!!

            if self.ACTIVITY_COUNT_TH_MIN != 0.0: current_value *= current_value > self.ACTIVITY_COUNT_TH_MIN
            if self.ACTIVITY_COUNT_TH_MAX != 1.0: current_value *= current_value < self.ACTIVITY_COUNT_TH_MAX

            self.avg = (self.avg * self.range_end + current_value) / (self.range_end+1)

            greater = (self.avg > self.max) * (-self.dec) * (self.avg-self.max)#/self.val_avg.range_end
            smaller = (self.avg < self.min) * (self.inc) * (self.min-self.avg)#/self.val_avg.range_end

            if self.target_attr != '':
                setattr(neurons, self.target_attr, np.clip(getattr(neurons, self.target_attr)+greater+smaller, self.target_min, self.target_max))
            #else:
            #    print(neurons.avg)

#class GABANormalization(TRENNeuronBehaviour):

#    def set_variables(self, neurons):
#        #neurons.GABA_norm_value = neurons.get_random_neuron_vec()*self.get_init_attr('GABA_norm_value', 1.0)
#        neurons.GABA_norm_value = neurons.get_neuron_vec() + self.get_init_attr('GABA_norm_value', 1.0, neurons)

#        #neurons.GABA_norm_value[0] = 10.0

#    def new_iteration(self, neurons):
#        if neurons.learning:
#            neurons.temp_weight_sum = neurons.get_neuron_vec()

#            for s in neurons.afferent_synapses['GABA']:
#                s.dst.temp_weight_sum += np.sum(s.GABA_Synapses, axis=1)
                #s.get_dest_vec('temp_weight_sum')[:] += np.sum(s.GABA_Synapses, axis=1)

#            neurons.temp_weight_sum /= neurons.GABA_norm_value

#            for s in neurons.afferent_synapses['GABA']:
#                #s.GABA_Synapses /= s.get_dest_vec('temp_weight_sum')[:, None]
#                #s.GABA_Synapses = np.clip(s.GABA_Synapses, 0, None)
#                print(s.get_dest_vec('temp_weight_sum')[:, None])



class GlutamateCacheConvergeAndNormalization(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Normalization')
        nv = self.get_init_attr('norm_value', 2.7, neurons)
        #neurons.norm_value = neurons.get_neuron_vec() + self.get_init_attr('norm_value', 2.7)
        #neurons.norm_value = neurons.get_random_neuron_vec()*self.get_init_attr('norm_value', 2.7)
        #neurons.norm_value = neurons.get_random_neuron_vec()*nv+0.0001
        neurons.weight_norm_factor = (neurons.get_neuron_vec()+1.0) * nv

        for s in neurons.afferent_synapses['GLU']:
            s.W = s.get_synapse_mat()

        self.new_iteration(neurons)


    def new_iteration(self, neurons):
        if neurons.learning:
            #neurons.temp_weight_sum = neurons.get_neuron_vec()

            for s in neurons.afferent_synapses['GLU']:
                s.W = np.sum(s.W_Caches, axis=0)

            normalize_synapse_attr('W', 'W_Caches', neurons.weight_norm_factor, neurons, 'GLU')

        for s in neurons.afferent_synapses['GLU']:
            s.W = np.clip(np.sum(s.W_Caches, axis=0), 0, None)#todo move to separate behaviour and do construction there


#only for LGN

class TREN_input_weighting(Behaviour):

    def set_variables(self, neurons):
        neurons.norm_value = neurons.get_random_neuron_vec()*0.5#0.4-0.2+0.3 #neurons.get_neuron_vec()+1

    def new_iteration(self, neurons):
        neurons.glu_inter_gamma_activity *= neurons.norm_value