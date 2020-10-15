training_steps=10000

input_width = 10
input_height = 10


activator = TRENNeuronPreprocessedActivator(write_to='glu_inter_gamma_activity')
img_patches=TNAP_Image_Patches(image_path='../Data/Images/bod_mainImg_01.jpg',grid_width=input_width, grid_height=input_height)
activator.add_patternGroups([img_patches])
LGN_PC_Neurons = NeuronGroup(input_width * input_height, {0: TRENNeuronDimension(input_width, input_height, 1), 1: activator, 2: ActivityBuffering(store_input=False, min_buffersize=2)})
activator.preprocess(training_steps, LGN_PC_Neurons)




#LGN_PC_Neurons = get_default_Input_Pattern_Neurons(input_width=10, input_height=10, preprocessing_steps=training_steps)

neu_rec = TRENNeuronRecorder(['output_activity_history[0]', 'input_activity_history[0]', 'activity', 'reward', 'norm_value'])

behaviour = {
    0: TRENNeuronDimension(2, 2, 1),

    1: InterGammaGlutamate(),
    3: IntraGammaGABA(),
    4: ActivityBuffering(),

    5: STDP(), #post_learn_value=0.0005
    6: TemporalWeightCache(decay=1, strength=1),
    7: HomeostaticMechanism(),

    8: GlutamateCacheConvergeAndNormalization(),#norm_value=4.5)
    9: neu_rec
}
Cortex_PC_Neurons = NeuronGroup(-1, behaviour)


feed_forward_syn = SynapseGroup(LGN_PC_Neurons, Cortex_PC_Neurons, 'src.x[s]<10 and src.y[s]<5').add_tag('GLU')

print(feed_forward_syn.enabled)

#recurrent_syn = TRENSynapseGroup(Cortex_PC_Neurons, Cortex_PC_Neurons).add_tag('GLU')
inh_syn = SynapseGroup(Cortex_PC_Neurons, Cortex_PC_Neurons, 's!=d').add_tag('GABA')


network = Network([LGN_PC_Neurons, Cortex_PC_Neurons], [feed_forward_syn, inh_syn])#inh_syn,recurrent_syn


start_TREN_UI(network, None)#['post_learn_value','exponent','pre_learn_value','firetreshold'])


#TPE=TREN_Pattern_Exploration(network, Cortex_PC_Neurons, feed_forward_syn)

#TPE.set_x_steps(Cortex_PC_Neurons, 'post_learn_value', 1.5, 3.5, 10, False)
#TPE.set_y_steps(Cortex_PC_Neurons, 'initial_norm_value', 0.0001, 0.1, 2, False)#*=...!

#TPE.start_iterations(training_steps)
