from PymoNNto.NetworkCore.Behavior import *

class Instant_Homeostasis(Behavior):

    def get_measurement_param(self, n):
        if self.compiled_mp is None:
            self.compiled_mp = compile(self.measurement_param, '<string>', 'eval')

        result = eval(self.compiled_mp)

        if self.measurement_min is not None: result = np.clip(result, self.measurement_min, None)
        if self.measurement_max is not None: result = np.clip(result, None, self.measurement_max)
        return result

    def add_to_target_param(self, neurons, add):
        val = getattr(neurons, self.adjustment_param)+add
        if self.target_clip_min is not None or self.target_clip_max is not None:
            val = np.clip(val, self.target_clip_min, self.target_clip_max)
        setattr(neurons, self.adjustment_param, val)


    def get_target_adjustment(self, measure_or_average):

        greater = (measure_or_average > self.max_th) * (-self.dec)
        smaller = (measure_or_average < self.min_th) * self.inc

        if self.distance_sensitive:
            greater *= measure_or_average - self.max_th
            smaller *= self.min_th - measure_or_average

        return (greater+smaller)*self.adj_strength

    def set_threshold(self, th, gap_percent=None):
        self.th = th #just for readout and copying

        if th is not None:
            self.min_th = th
            self.max_th = th

            if gap_percent is not None:
                self.min_th -= self.min_th/100*gap_percent
                self.max_th += self.max_th/100*gap_percent


    def initialize(self, neurons):

        self.compiled_mp=None

        self.min_th = self.parameter('min_th', None, neurons)                           #minumum threshold for measurement param
        self.max_th = self.parameter('max_th', None, neurons)                           #maximum threshold for measurement param

        self.set_threshold(                                                                 #optional
            self.parameter('threshold', None, neurons),                                 #threshold for measurement param (min=max=th)
            self.parameter('gap_percent', None, neurons)                                #min max gap is created via a percentage from th (additional param for th)
        )

        self.distance_sensitive = self.parameter('distance_sensitive', True, neurons)   #stronger adjustment when value is further away from optimum

        self.inc = self.parameter('inc', 1.0, neurons)                                  #increase factor
        self.dec = self.parameter('dec', 1.0, neurons)                                  #decrease factor
        self.adj_strength = self.parameter('adj_strength', 1.0, neurons)                #change factor

        self.adjustment_param = self.parameter('adjustment_param', None, neurons)       #name of neurons target attribute

        self.measurement_param = self.parameter('measurement_param', None, neurons)     #name of parameter to be measured

        self.measurement_min = self.parameter('measurement_min', None, neurons)         #minumum value which can be measured (below=0)
        self.measurement_max = self.parameter('measurement_max', None, neurons)         #maximum value which can be measured (above=max)

        self.target_clip_min = self.parameter('target_clip_min', None, neurons)         #target clip min
        self.target_clip_max = self.parameter('target_clip_max', None, neurons)         #target clip max


    def iteration(self, neurons):
        measure_or_average = self.get_measurement_param(neurons)
        self.add = self.get_target_adjustment(measure_or_average)
        self.add_to_target_param(neurons, self.add)


class Time_Integration_Homeostasis(Instant_Homeostasis):

    def get_measurement_param(self, n):

        value = super().get_measurement_param(n)
        self.average = (self.average * self.integration_length + value) / (self.integration_length+1)
        return self.average

    def initialize(self, neurons):
        super().initialize(neurons)

        self.integration_length = self.parameter('integration_length', 1, neurons)      #factor that determines the inertia of the leaky integrator (0=instant) (a*i)/(1+i)

        self.average = self.parameter('init_avg', (self.min_th+self.max_th)/2, neurons)                          #initialize average measurement for each neuron

#Time_Integration_Homeostasis().visualize_module(vmi=['measure'], vmo=['adjust'], vma=['measurement_param','adjustment_param','threshold','integration_length','...'])