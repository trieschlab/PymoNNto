from PymoNNto.Exploration.AnalysisModules.Weight_Classifier_Base import *

class Weight_Classifier_Post(Classifier_base):

    def get_data_matrix(self, neurons):
        syn_tag = self.parameter('syn_tag', 'EE')
        return get_partitioned_synapse_matrix(neurons, syn_tag, 'W')
