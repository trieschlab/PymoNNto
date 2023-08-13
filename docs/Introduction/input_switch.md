# Input switching

This is an example how to implement an experiment with alternating training and testing stimuli.

```python
trainging_stimulus = ...
testing_stimulus = ...

NeuronGroup(...,  behavior={..., 
            1: InputStimulus(tag='train', stimulus=trainging_stimulus),
            2: InputStimulus(tag='test', stimulus=testing_stimulus),
            # ...
            9: Recorder(tag="rec", variables=["n.v", "n.fired"]),
})
               
# initialize

for loop in range(loop_count):
        network.activate_mechanisms('train')
        network.deactivate_mechanisms('test')
        network.train.index = 0 # [tag,0] is equivalent to [tag][0] and gives you the first found object with the given tag
        network.simulate_iterations(len(trainging_stimulus))
        recorded = network["n.fired", 0] 
        network.rec.reset()

        network.deactivate_mechanisms('train')
        network.activate_mechanisms('test')
        network.test.index = 0
        network.simulate_iterations(len(testing_stimulus))
        recorded = network["n.v", 0]
        network.rec.reset()

#increase the self.index variable inside of the InputStimulus module at each step.
```
