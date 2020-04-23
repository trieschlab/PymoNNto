from NetworkBehaviour.Input.Images.Helper import *
from NetworkCore.Base import *
from NetworkBehaviour.Input.Pattern_Basics import *

class Pixel_Pattern(PatternGroup):

    def initialize(self):
        self.patterns = []
        self.labels = []

        self.lastpattern = None
        self.pattern_show_duration_counter = 0
        self.pattern_duration_cycles = self.kwargs.get('pattern_duration_cycles', 1)

        self.individual_possibility = self.kwargs.get('individual_possibility', 0.0)
        self.overlapping_within_group = self.kwargs.get('overlapping_within_group', False)

        self.value_mode = self.kwargs.get('value_mode', 'fixed_value_mode')

        self.grid_width = self.kwargs.get('grid_width', 1)
        self.grid_height = self.kwargs.get('grid_height', 1)
        self.grid_channels = self.kwargs.get('grid_channels', 1)

        self.mask_mode = self.kwargs.get('mask_mode', 'center')

        self.select_mode = self.kwargs.get('grid_channels', 'sequential')
        self.select_counter=-1

    def get_current_pattern_index(self):

        if self.select_mode == 'random':
            return np.random.randint(len(self.patterns))

        if self.select_mode == 'sequential':
            self.select_counter+=1
            if self.select_counter>=len(self.patterns):
                self.select_counter=0
            return self.select_counter

    def initialize_neuron_group(self, neurons):

        if self.mask_mode == 'first':
            neurons.Input_Mask = np.arange(neurons.size)<self.get_pattern_length()

        if self.mask_mode == 'random':
            chosen=np.random.choice(np.arange(neurons.size), self.get_pattern_length(), replace=False)
            neurons.Input_Mask = [(nr in chosen) for nr in np.arange(neurons.size)]

        if self.mask_mode == 'center':
            neurons.Input_Mask = (neurons.x < self.grid_width/2)*(neurons.x >= -self.grid_width/2)*(neurons.y < self.grid_height*self.grid_channels/2)*(neurons.y >= -self.grid_height*self.grid_channels/2)

    def get_pattern(self, neurons):

        self.current_pattern_index = -1

        if self.active:
            self.pattern_show_duration_counter -= 1
            if self.pattern_show_duration_counter > 0:
                return self.lastpattern

            result = None
            if len(self.patterns) > 0:
                result = neurons.get_neuron_vec()

                if self.overlapping_within_group:
                    self.current_pattern_index = []
                    for i, pattern in enumerate(self.patterns):
                        if np.random.rand() < self.individual_possibility:
                            result[neurons.Input_Mask] += self.get_pattern_values(pattern).flatten()
                            self.current_pattern_index.append(i)
                else:
                    r = self.get_current_pattern_index()
                    self.current_pattern_index = r
                    result[neurons.Input_Mask] += self.get_pattern_values(self.patterns[r]).flatten()

                self.lastpattern = result
                self.pattern_show_duration_counter = self.pattern_duration_cycles

            return result
        else:
            return None

    def get_pattern_values(self, pattern):
        if pattern.shape != self.get_pattern_dimension():
            x = np.random.randint(pattern.shape[2] - self.grid_width)
            y = np.random.randint(pattern.shape[1] - self.grid_height)
            return pattern[:, y:y + self.grid_height, x:x + self.grid_width]
        else:
            return pattern

    def get_vstackpattern_dimension(self):
        dim = self.get_pattern_dimension()
        return (dim[0] * dim[1], dim[2])

    def get_pattern_dimension(self):
        return (self.grid_channels, self.grid_height, self.grid_width)

    def get_pattern_length(self):
        return self.grid_channels*self.grid_height*self.grid_width

    def reconstruct_pattern(self, p):
        return p.reshape(self.get_pattern_dimension())