from PymoNNto.Exploration.AnalysisModules.Weight_Classifier_Base import *

class Weight_Classifier_Pre(Classifier_base):

    def get_data_matrix(self, neurons):
        syn_tag = self.get_init_attr('syn_tag', 'EE')
        return get_partitioned_synapse_matrix(neurons, syn_tag, 'W').T