# Homeostasis

This mechanism can be used to stabilize the neurons activity.

When the voltage of a neuron is above the maximum target activity, max_ta, the exhaustion value increases.
When the voltage is below min_ta, the exhaustion value decreases.
The exhaustion value changes faster, the further away the voltage is from the corresponding threshold.
When the voltage is between both thresholds the exhaustion variable stays unchanged.
The speed of increase and decrease is defined by the parameter adj_strength.
In case only a single value should define the target rate the user can directly make use of the target_act variable.
In that case, min_ta and max_ta are both set to this value.
The area between min_ta and max_ta can be useful to dampen oscillations inside of the network.

The same homeostatic principle can be used in different contexts.
Instead of regulating the voltage, the module can be repurposed to increase or decrease the sizes of the neurons synapses, to regulate the firing threshold or to dynamically adapt a plasticity rule.
All this requires only minor modifications.

<img width="300" src="https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Homeostasis.png"><img width="300" src="https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/HM_vg.png"><br>

```python
# /Examples_Paper/STDP_Hom_Norm/Homeostasis.py
from PymoNNto.NetworkCore.Behavior import *

class Homeostasis(Behavior):

    def initialize(self, neurons):
        target_act = self.parameter('target_voltage', 0.05, neurons)

        self.max_ta = self.parameter('max_ta', target_act, neurons)
        self.min_ta = self.parameter('min_ta', target_act, neurons)

        self.adj_strength = -self.parameter('eta_ip', 0.001, neurons)

        neurons.exhaustion = neurons.vector()



    def iteration(self, neurons):

        greater = ((neurons.voltage > self.max_ta) * -1).astype(neurons.def_dtype)
        smaller = ((neurons.voltage < self.min_ta) * 1).astype(neurons.def_dtype)

        greater *= neurons.voltage - self.max_ta
        smaller *= self.min_ta - neurons.voltage

        change = (greater + smaller) * self.adj_strength
        neurons.exhaustion += change

        neurons.voltage -= neurons.exhaustion
```