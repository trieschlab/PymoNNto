#Sidebar Activity
The activity module can display neurons in a grid with different colors for different neuron variables. The variables and their colors can be definded with the dictionary given to the tab constructor. 
The base color is determined by the MyNeuronGroup.color value.
The module is also required for different other modules because it can be used to select individual neurons which are then shown in green.
The top drop down menu can be used to select different NeuronGroups and the slider to the right can be used to change different attributes of this selected group in other tabs.
```python
UI_sidebar_activity_module(1, add_color_dict={'voltage':(255, 255, 255)})
```
![Sidebar_Activity](https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Sidebar_Activity.png)
#Multi Group Tab
The multi group tab can display the mean of some NeuronGroup variables and of individual neurons over time. 
Multiple Groups can can be displayed at the same time, so their variables, like their average activity can be compared. 
The sliders in the activity modules can be used to squeeze the graphs on top of each other which does only change the visualization.
The list of NeuronGroup variables can be definded with the list passed to the constructor.
```python
multi_group_plot_tab(['output'])
```
![Multi_Group_Tab](https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Multi_Group_Tab.png)
#Spiketrain Tab
The spiketrain tab can be used to visualize a variable of all neurons of some NeuronGroups over time. 
On the x axis we can see individual timesteps while the y axis represents individual neuorns.
The selected neuron is highlighted with a brighter bar.
```python
spiketrain_tab(parameter='output')
```
![Spiketrain_Tab](https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Spiketrain_Tab.png)
#Weight Tab
The weight tab can visualize some variables of the the afferent synapses of the selected neuron. The SynapseGroup variables(matrix) can be defined in the constructor.
```python
weight_tab(weight_attrs=['W'])
```
![Weight_Tab](https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Weight_Tab.png)
#Partition_Tab
To speed up the processing of sparse synapse matrices, PymoNNto can split a NeuronGroup into subgroups when creating a new SynapseGroup. This can be useful when the neurons have receptive fields, for example.
This partition tab can visualize a partitioned SynapseGroup.
On the left of the arrow we always see the source neurons of the synapse and on the right the destination. 
We can interactively select some destination subgroups and see their maximum receptive field limited by the partition algorithm.
```python
partition_tab()
```
![Partition_Tab](https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Partition_Tab.png)
#PCA Tab
The PCA Tab can display the singular values of some NeuronGroup vector recorded over the last timesteps (1000 by default).
We see the current singular values (top left), the percentage explained by the biggest x features (top right) and the 5 biggest features over time.
```python
PCA_tab(parameter='output')
```
![PCA_Tab](https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/PCA_Tab.png)
#Weight Distribution Tab
The weight distribution tab can visualize histograms of the afferent weights of a NeuronGroup and its selected Neuron (green).
The afferent Synapses are automatically sorted into rows for each transmitter type (first tag of the SynapseGroup). 
Multiple SynapseGroups with the same tag are combined and handeled like one big synapse matrix.
The NeuronGroup can be subdivided into two groups with a mask_param vector which can be used to differentiate between neurons with and without external input, for example.
With the sliders we can cut off very small synapses and change the number of bins of the visualized histograms.
The synapse parameter (matrix) can be definded in the constructor.
```python
hist_tab(weight_attr='W') #, mask_param='Input_Mask'
```
![Weight_Distribution_Tab](https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Weight_Distribution_Tab.png)
#Single Group Tab
The single group plot tab can be used to visualize multiple variables within one NeuronGroup and in the selected neuron. 
All variables can be cosen in the constructor with an individual color and they are all visualized in one plot for a better comparison.
```python
single_group_plot_tab({'output':(0, 0, 0), 'voltage':(0, 255, 0)})
```
![Single_Group_Tab](https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Single_Group_Tab.png)
#Stability Tab
The stability tab visualizes the autocorrelation of some variable in one and between different NeuronGroups.
The x axis represents the value at timestep t and the y axis the next value at timestep t+1. When there are no oscillations in a Group, we should see a single dot. 
When the oscillations are very weak, we see a diagonal cloud from bottom left to the upper right corner while strong oscillations tend to create orthogonal clouds. 
```python
stability_tab(parameter='output')
```
![Stability_Tab](https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Stability_Tab.png)
#Fourier Tab
The fourier tab does a fourier transformation of the activity trace of the given variable. 
The x axis is divided into alpha, beta, gamma, ... bands. Because the simulation performs discrete timesteps without a "time" unit, we can select this unit with the slider below. 
The other sliders can cut off the lowest frequencies and smooth the plot to a certain degree.
```python
fourier_tab(parameter='output')
```
![Fourier_Tab](https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Fourier_Tab.png)
#Info Tab
The info tab can monitor and change the NeuronGroup behaviour attributes during the simulation. 
All attributes passed to the behaviour during its construction can be seen and changed by clicking on the blue link-like text. 
This opens a drop down menu where we can change the individual attributes. 
When we click the update button we basically call the set_variables function of the given behaviour a second time, which should reset and re-initialize the given behaviour. 
Note that only the set_variables functions of the selected behaviours is updated, which can lead to problems, when different behaviours have to be initialized in a specific order.

```python
info_tab()
```
![Info_Tab](https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Info_Tab.png)
#Sidebar Fast Forward
The fast forward module can start, pause, and fast forward the simulation without ui updates. The checkbox defines whether the recorders are active during the this fast iterations.
```python
sidebar_fast_forward_module()
```
![Sidebar_Controll](https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Sidebar_Controll.png)
#Sidebar Save Load
The save load module can be used to save and load individual network states. The filename can be defined in the textbox while the drop down menu displays states that are ready to load.
```python
sidebar_save_load_module()
```
![Sidebar_save_load](https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Sidebar_save_load.png)