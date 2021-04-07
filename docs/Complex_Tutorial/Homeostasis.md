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

![User interface example](https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/HM_vg.png)

```python
from PymoNNto.NetworkCore.Behaviour import *

class Homeostasis(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Homeostatic_Mechanism')

        target_act = self.get_init_attr('target_voltage', 0.05, neurons)

        self.max_ta = self.get_init_attr('max_ta', target_act, neurons)
        self.min_ta = self.get_init_attr('min_ta', target_act, neurons)

        self.adj_strength = -self.get_init_attr('eta_ip', 0.001, neurons)

        neurons.exhaustion = neurons.get_neuron_vec()



    def new_iteration(self, neurons):

        greater = ((neurons.voltage > self.max_ta) * -1).astype(def_dtype)
        smaller = ((neurons.voltage < self.min_ta) * 1).astype(def_dtype)

        greater *= neurons.voltage - self.max_ta
        smaller *= self.min_ta - neurons.voltage

        change = (greater + smaller) * self.adj_strength
        neurons.exhaustion += change

        neurons.voltage -= neurons.exhaustion
```