# Tensorflow Modules

```python
class STDP_TF(TensorflowBehaviour):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.add_tag('STDP_TF')

        neurons.output = tf.Variable(neurons.vector(), dtype='float32')
        neurons.output_old = tf.Variable(neurons.vector(), dtype='float32')

        neurons.eta_stdp = tf.constant(self.parameter('eta_stdp', 0.00015, neurons), dtype='float32')

        self.syn_type = self.parameter('syn_type', 'GLU', neurons)

    def new_iteration(self, neurons):

        for s in neurons.afferent_synapses[self.syn_type]:

            pre_post = tf.tensordot(s.dst.output, s.src.output_old, axes=0)
            simu = tf.tensordot(s.dst.output, s.src.output, axes=0)
            post_pre = tf.tensordot(s.dst.output_old, s.src.output, axes=0)

            dw = tf.multiply(neurons.eta_stdp, tf.add(tf.subtract(pre_post, post_pre), simu))

            s.W.assign(tf.clip_by_value(tf.add(s.W, tf.multiply(dw, s.enabled)), 0.0, 1.0))
```