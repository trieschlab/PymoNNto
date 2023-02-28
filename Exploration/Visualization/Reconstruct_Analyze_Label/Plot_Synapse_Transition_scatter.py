import sys
sys.path.append('../../../TREN2')
sys.path.append('../../../tren2')
from PymoNNto.Exploration.StorageManager.StorageManager import *


smg = StorageManagerGroup('SORN_Gram_train_time_100k')# SORN_One_layer_all_600

x=[]
y=[]

for ms_i, sm in enumerate(smg.StorageManagerList):
    try:
        network = sm.load_obj('net')
        source = sm.load_obj('source')
        network.NeuronGroups = [network.NeuronGroups[0]]
        network.SynapseGroups = [network.SynapseGroups[0]]
        groups = [network.NeuronGroups[0]]
        RALN = Reconstruct_Analyze_Label_Network(network)
        RALN.label_and_group_neurons(network.NeuronGroups[0],
                                     [source.get_activation(char) for char in range(source.get_alphabet_length())], 'W', 10)

        trans = RALN.get_synapse_transition_dict(source, x_attribute_name='temporal_layer',
                                                 y_attribute_name='class_label',
                                                 weight_attribute_name='W', groups=groups, weight_limit=1 / 3)

        freq, ocd, filtered_trans = RALN.get_transition_frequencies(trans, source)
        print(ocd)
        classes = RALN.get_transition_classes(trans, freq)

        x_n, y_n = RALN.plot_transition_frequencies(filtered_trans, freq, plot_single=True, plot_multiple=True, show_labels=True, network=network)

        print(x_n)

        x+=list(x_n)
        y+=list(y_n)


        #plt.show()
        # RALN.plot_bars(filtered_trans)
        # plt.xlabel('label')
        # plt.ylabel('synapses')
        # plt.show()
        # RALN.plot_bars(classes)
        # plt.xlabel('label')
        # plt.ylabel('synapses')
        # plt.show()

        #print(sm.absolute_path)
        #sm.save_param_dict()
    except Exception as e:
        print('not able to load network or source',e)
    if ms_i > 0:
        break

#print(np.array(x).flatten().shape,np.array(y).flatten().shape)

RALN.draw_trend_line(np.array(x).flatten(), np.array(y).flatten())

plt.xlabel('synapses')
plt.ylabel('found in text')
#plt.xscale('log')
#plt.xscale('log')
plt.show()
#todo fix text occurences vs num of synapses!!!
#todo