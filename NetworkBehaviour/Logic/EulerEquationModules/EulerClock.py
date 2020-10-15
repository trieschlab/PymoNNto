from NetworkCore.Neuron_Behaviour import *

class SORN_generate_output_K_WTA_partitioned(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('K_WTA_partitioned')

        self.filter_temporal_output = self.get_init_attr('filter_temporal_output', False, neurons)

        neurons.output = neurons.get_neuron_vec()

        self.K = self.get_init_attr('K', 0.1, neurons)#only accepts values between 0 and 1

        partition_size = self.get_init_attr('partition_size', 7, neurons)
        self.partitioned_ng=neurons.partition_size(partition_size)

    def new_iteration(self, neurons):