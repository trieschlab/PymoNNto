from Exploration.Visualization.Reconstruct_Analyze_Label.Reconstruct_Analyze_Label import *
from NetworkBehaviour.Recorder.StorageManager import *

#sm = StorageManager('X_1', 'X')
#sm = StorageManager('RALN_Test_2_0', 'RALN_Test_2')
#sm = StorageManager('MemoryCapacity_2', 'MemoryCapacity')#('RALN_Test_MT_Small_0', 'RALN_Test_MT_Small')

#sm = StorageManager('SORN_One_layer_all_600_0', 'SORN_One_layer_all_600')

#sm = StorageManager('SORN_Two_layer_all_600_0', 'SORN_Two_layer_all_600')
sm = StorageManager('SORN_New_Grammar_test', 'SORN_New_Grammar_test_35')#11

#plt.plot([sm.load_param('error_{}'.format(i)) for i in range(20)])
#plt.show()

weight_limit = None#1/3#None#1/3#0.5
n_biggest = 3#None

network = sm.load_obj('net')

network.NeuronGroups = [network.NeuronGroups[0]]
network.SynapseGroups = [network.SynapseGroups[0]]

source = sm.load_obj('source')

RALN = Reconstruct_Analyze_Label_Network(network)

#max_lag = np.max([ng.iteration_lag for ng in network.NeuronGroups])
#for ng in network.NeuronGroups:
#    ng.color = (0, 0, 1/max_lag*ng.iteration_lag)

groups = [network.NeuronGroups[0]]#, network.NeuronGroups[1]
RALN.label_and_group_neurons(network.NeuronGroups[0], [source.get_activation(char) for char in range(source.get_alphabet_length())], 'W', 10)

#max_vec, distribtuion, avg = RALN.get_all_buffer_length_distribution(groups)
#print(max_vec, distribtuion, avg)
#w = 1/(len(distribtuion)+10)
#for i, d in enumerate(distribtuion):
#    plt.bar(np.arange(len(d))+((w)*(i+5))-0.5, d, width=w)
#plt.plot(np.average(np.array(distribtuion), axis=0))
#plt.show()
#RALN.analyze_synapses(source, x_attribute_name='temporal_layer', y_attribute_name='class_label', weight_attribute_name='W', groups=groups, weight_limit=1/3, visualize=True)



RALN.visualize_label_and_group_neurons(x_attribute_name='temporal_layer', y_attribute_name='class_label', weight_attribute_name='W', groups=groups, weight_limit=weight_limit, n_biggest=n_biggest, source=source)
trans = RALN.get_synapse_transition_dict(source, x_attribute_name='temporal_layer', y_attribute_name='class_label', weight_attribute_name='W', groups=groups, weight_limit=weight_limit, n_biggest=n_biggest)

freq, ocd, filtered_trans = RALN.get_transition_frequencies(trans, source)
classes = RALN.get_transition_classes(trans, freq)
RALN.plot_bars(filtered_trans)
plt.xlabel('label')
plt.ylabel('synapses')
plt.show()
RALN.plot_bars(classes)
plt.xlabel('label')
plt.ylabel('synapses')
plt.show()



