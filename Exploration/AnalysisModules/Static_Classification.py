from PymoNNto import *

class Static_Classification(AnalysisModule):

    def initialize(self, neurons):
        self.add_tag('classifier')
        self.name = self.parameter('name', super()._get_base_name_())
        classes = self.parameter('classes', None) #array with size neurons.size where each entry is a number that defines the neurons class
        self.save_result(self.name, classes) #stored in the results array (one classifier can generate multiple classifications)

    def _get_base_name_(self):
        return self.name
