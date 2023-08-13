# Compact Conditional Behavior Attachment

Only works with python 3.9 or higher!

Here we see how the | operator, which connects dictionaries, can be used to conditionally attach behaviors.
Behavior5 is only attached to the NeuronGroup in the first layer, otherwise it will get skipped.

```python
NeuronGroup(..., tag='neurons_'+str(layer), behavior={
    1: Behavior1(),
    2: Behavior2(),
    3: Behavior3(),
    
}|({5: Behavior5()} if layer==1 else {})|{

    7: Behavior7(),
    8: Behavior8(),
    9: Behavior9()
})
```

