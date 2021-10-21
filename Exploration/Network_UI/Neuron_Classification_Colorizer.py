from PymoNNto.NetworkCore.Analysis_Module import *

class Neuron_Classification_Colorizer(AnalysisModule):

    def initialize(self, neurons):
        self.add_tag('colorizer')
        self.unique_colors = {}
        self.compiled_formats = {}

    def get_color_list(self, neuron_class_list, format='[r,g,b,255.0]'):
        if neuron_class_list is None:
            neuron_class_list = np.zeros(self.parent.size)
        color_dict = self.get_class_color_dict(neuron_class_list, format)
        return [color_dict[neuron_class_list[c]] for c in range(self.parent.size)]

    def get_class_color_dict(self, neuron_class_list, format='[r,g,b,255.0]'):
        unique = np.unique(neuron_class_list)
        colors = self.get_unique_colors(len(unique), format=format)
        return dict(zip(unique, colors))

    def get_unique_colors(self, number, format='[r,g,b,255.0]'):#[r,g,b,a]
        if not format in self.unique_colors:
            self.unique_colors[format] = []
            self.compiled_formats[format] = compile(format, '<string>', 'eval')

        comp = self.compiled_formats[format]
        rnd_r = 'r' in format
        rnd_g = 'g' in format
        rnd_b = 'b' in format
        rnd_a = 'a' in format

        while len(self.unique_colors[format]) < number:
            if rnd_r: r = np.random.rand()*255.0
            if rnd_g: g = np.random.rand()*255.0
            if rnd_b: b = np.random.rand()*255.0
            if rnd_a: a = np.random.rand()*255.0

            if hasattr(self.parent, 'color'):
                if len(self.unique_colors[format]) == 0:
                    r = self.parent.color[0]
                    g = self.parent.color[1]
                    b = self.parent.color[2]
                if len(self.unique_colors[format]) == 1:
                    r = self.parent.color[0]*0.6
                    g = self.parent.color[1]*0.6
                    b = self.parent.color[2]*0.6
                if len(self.unique_colors[format]) == 2:
                    r = self.parent.color[0]*0.3
                    g = self.parent.color[1]*0.3
                    b = self.parent.color[2]*0.3

            self.unique_colors[format].append(eval(comp))
        return self.unique_colors[format]
