
```python

from PymoNNto.NetworkBehaviour.Basics.BasicHomeostasis import *



class NOX_Diffusion(Instant_Homeostasis):

    def partition_sum(self, neurons):
        neurons._temp_act_sum = neurons.vector()
        for sg, sg_rf in zip(self.subgroups, self.subgroups_rf):
            sg._temp_act_sum += np.mean(sg_rf.output_new)
        return neurons._temp_act_sum

    def set_variables(self, neurons):
        super().set_variables(neurons)

        self.subgroups = self.split_grid_into_sub_group_blocks(steps=[5, 5, 1])

        receptive_field = 5
        self.subgroups_rf = []
        for sg in self.subgroups:
            sg_rf = neurons.get_subgroup_receptive_field_mask(sg, [receptive_field, receptive_field, receptive_field])
            self.subgroups_rf.append(sg_rf)

        neurons.nox = neurons.vector()
        self.adjustment_param = 'nox'

        self.measurement_param = self.parameter('mp', 'self.partition_sum(n)', None)

        self.set_threshold(self.parameter('th_nox', 0, neurons))
        self.adj_strength = -self.parameter('eta_nox', 0.002, neurons)

    def new_iteration(self, neurons):
        neurons.nox.fill(0)
        super().new_iteration(neurons)


```