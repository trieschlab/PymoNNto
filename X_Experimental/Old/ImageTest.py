from Testing.TREN.Helper import *

iterations = 10000
input_width = 10
input_height = 10

activator = NeuronActivator(write_to='glu_inter_gamma_activity')

#lines1 = TNAP_Lines(group_possibility=1.0, grid_width=input_width, grid_height=input_height, center_x=input_width / 2,
#                    center_y=list(range(input_height)), degree=0, line_length=input_width + input_height)
#lines2 = TNAP_Lines(group_possibility=1.0, grid_width=input_width, grid_height=input_height, center_x=list(range(10)),
#                    center_y=input_height / 2, degree=90, line_length=input_width + input_height)
#activator.add_patternGroups([lines1, lines2])

#noise = TNAP_Noise(size=input_width * input_height, density=0.01)
img_patches = TNAP_Image_Patches(image_path='../Data/Images/pexels-photo-275484.jpeg', grid_width=input_width, grid_height=input_height, dimensions=['off_center_white', 'on_center_white', 'rgbw', '255-rgbw'], patch_norm=False)#'red', 'green', 'blue', 'gray', '255-red', '255-green', '255-blue', '255-gray'
activator.add_patternGroups([img_patches])

LGN_PC_Neurons = NeuronGroup(input_width * input_height, {0: NeuronDimension(input_width, input_height, img_patches.z_dim), 1: activator, 2: ActivityBuffering(store_input=False, min_buffersize=2)})  #

print(LGN_PC_Neurons.size)

#neu_rec = TRENNeuronRecorder(['output_activity_history[0]', 'input_activity_history[0]', 'activity'])#activity

behaviour = {
    0: NeuronDimension(input_width, input_height, 1),

    1: InterGammaGlutamate(),
    4: ActivityBuffering(),
    5: STDP(post_learn_value=0.03),
    6: TemporalWeightCache(decay=1, strength=1),
    7: HomeostaticMechanism(),
    8: GlutamateCacheConvergeAndNormalization()#norm_value=2.7
    #9:neu_rec
    #syn_rec
}
Cortex_PC_Neurons = NeuronGroup(-1, behaviour)


feed_forward_syn = SynapseGroup(LGN_PC_Neurons, Cortex_PC_Neurons).add_tag('GLU')
recurrent_syn = SynapseGroup(Cortex_PC_Neurons, Cortex_PC_Neurons, 's!=d').add_tag('GLU')
inh_syn = SynapseGroup(Cortex_PC_Neurons, Cortex_PC_Neurons).add_tag('GABA')


network = Network([LGN_PC_Neurons, Cortex_PC_Neurons], [feed_forward_syn, inh_syn])

plot_reconstruction_activations(LGN_PC_Neurons[NeuronActivator].get_pattern_samples(100), 10, 10 * img_patches.z_dim)
plt.show()

#rec=network.get_reconstruction(Cortex_PC_Neurons, list(range(1)), LGN_PC_Neurons, 'GLU_Synapses', 1)#{'GLU_Synapses':1,'GABA_Synapses':-1}, just_nuerons=[] just_synapses=[]
#network.plot_reconstruction_activations(rec, 10, 10)
#plt.show()


#pat=network.get_reconstruction(Cortex_PC_Neurons,[1,2,3],LGN_PC_Neurons,'GLU_Synapses',1)[0]
#print(LGN_PC_Neurons[TRENNeuronActivator].get_pattern_differences(pat))

#image = network.get_whole_Network_weight_image(Cortex_PC_Neurons, neuron_src_groups=None)
#plt.imshow(image, interpolation="nearest")
#plt.show()

network.simulate_iterations(100, iterations/100, True)


#pat=network.get_reconstruction(Cortex_PC_Neurons, [1, 2, 3], LGN_PC_Neurons, 'GLU_Synapses', 1)[0]
#print(LGN_PC_Neurons[TRENNeuronActivator].get_pattern_differences(pat))

image = get_whole_Network_weight_image(Cortex_PC_Neurons, neuron_src_groups=None)
plt.imshow(image, interpolation="nearest")
plt.show()



#print(Cortex_PC_Neurons.t)

#rec=network.get_reconstruction(Cortex_PC_Neurons, list(range(10)), LGN_PC_Neurons, 'GLU_Synapses', 1)#{'GLU_Synapses':1,'GABA_Synapses':-1}, just_nuerons=[] just_synapses=[]
#activator.get_pattern_differences(pat)


#network.plot_reconstruction_activations(rec, 10, 10)
#plt.show()

#plt.plot(neu_rec.activity)
#plt.show()

#n_act=n_act[8000:-1]


#v = Visualizer(None)
#sys.exit(v.app.exec_())


#fig = plt.figure()
#ax = fig.add_subplot(111)
#plot_histogram(ax, n_act, 40)
#plt.show()