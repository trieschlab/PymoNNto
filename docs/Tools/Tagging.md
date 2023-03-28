## Tagging System

To access the tagged objects we can use the `[]` operator. `['my_tag']` gives you a list of all objects tagged with `my_tag`. Here are some examples:

```python
My_Network['my_neurons']
=> [<PymoNNto.NetworkCore.Neuron_Group.NeuronGroup object at 0x00000195F4878670>]

My_Network['my_recorder']
My_Neurons['my_recorder'] 
=> [<PymoNNto.NetworkBehavior.Recorder.Recorder.Recorder object at 0x0000021F1B61D5E0>]

My_Neurons['activity']
My_Neurons['my_recorder', 0]['activity']
=> [[array(data iteration 1), array(data iteration 2), array(data iteration 3), ...]]

My_Neurons['activity', 0] 
is equivalent to 
My_Neurons['activity'][0] 
```