from NetworkBehaviour.Input.Pattern_Basics import *

class Noise_Pattern(PatternGroup):

    def initialize(self):
        self.density = self.kwargs.get('density', 0.1)
        self.binary = self.kwargs.get('binary', True)
        self.max = self.kwargs.get('max', 1)
        self.min = self.kwargs.get('min', 0)

    def get_pattern(self, neurons):
        result=(np.random.rand(self.grid_channels, self.grid_height, self.grid_width)<self.density).astype(np.float64)
        if not self.binary:
            result*=np.random.rand(self.size)
        return self.min+result*self.max
