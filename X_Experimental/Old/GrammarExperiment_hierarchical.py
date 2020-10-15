#import sys
#sys.path.append('.')
#sys.path.append('../../../TREN2')
#sys.path.append('../../../tren2')

from Testing.Old.SORN_simple_behaviour import *

display = True

def run(ind=[]):
    print(ind)

    for i in range(1):
    #while True:
    #if True:

        #for N_e in [100, 200, 300, 600, 1000, 1400]:#:#[1,2,3,4,6,8,10,12,14,16,18,20,22,24,26,28,30]:#[2, 6, 10, 14, 16, 20]:#[16]
        for N_e in [1000]:

            synapses = 200
            #N_e = 1000
            #synapses = 10

            sm = StorageManager('learning_test_new', random_nr=False, print_msg=display)

            #layers = 3

            sm.save_param('N_e', N_e)
            sm.save_param('synapses', synapses)

            steps_plastic = 100000  # sorn training time steps #100000
            steps_readout = 10000  # readout train and test steps#10000
            steps_spont = 10000  # steps of spontaneous generation#10000

            sm.save_param('steps_plastic', steps_plastic)
            sm.save_param('steps_readout', steps_readout)
            sm.save_param('steps_spont', steps_spont)

            # source = TextActivator(N_e=N_e)
            # source = GrammarActivator(N_e=N_e)
            # source = TestTextActivator(N_e=N_e)

            #source = LongDelayGrammar(output_size=N_e, random_blocks=True)

            #source = ComplexGrammarActivator(output_size=N_e, random_blocks=True)
            source = FDTGrammarActivator_New(output_size=N_e, random_blocks=True)
            #source.print_test()
            #source = TextActivator_New(output_size=N_e, filename='../../Data/TextCorpora/SPD.txt', replace_dict={'?': '.', ':': '.', ',': '.', '.': '. ', '  ': ' ', '-': ''}, random_blocks=False)
            #source = TextActivator_New(max_iterations=600000, output_size=N_e, filename='../../Data/TextCorpora/CHILDES.txt', replace_dict={' PERIOD': '.', ' COMMA': ',', ' QUESTION': '?', ' EXCLAIM': '!', ' xxx': '', '^': '', '_': '', '™': '', '€': '', 'â': '', '&': '', '1': '', '2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '', '0': '', '[': '', ']': '', '=': '', '-': '', '+': '', '  ': ' '}, random_blocks=False)

            #source2 = Random_Text_Activator(output_size=N_e, random_blocks=True, alph=source.alphabet)
            #source2 = FDTGrammarActivator_New_shuffle(output_size=N_e, random_blocks=True)
            #source2.W=source.W

            if display:
                #source2.print_test()
                source.print_test()
                print(source.get_alphabet_length())


            #source = FDTGrammarActivator(N_e=int(N_e/adjustment))#Delayed_FDTGrammarActivator(N_e=N_e, delay=default__neuron_iterations)#FDTGrammarActivator #todo only for test

            SORN_layers_e = []
            SORN_layers_i = []
            ee_syns = []
            ie_syns = []
            ei_syns = []

            ee_forward_syns = []
            ee_backward_syns = []
            ie_forward_syns = []
            ie_backward_syns = []


            for i in [0]:#[0,1,3]:#range(layers):
                lag = i#+default__neuron_iterations-1#todo: only for test
                #print(N_e)

                SORN_layers_e.append(NeuronGroup(size=N_e, behaviour={
                    1: SORN_Input_collect(T_min=0.0, T_max=0.5, lamb=synapses, iteration_lag=lag + 1, fixed_synapse_count=False),
                    #2: SORN_STDP(eta_stdp='[0.005#0]', prune_stdp=False),
                    #3: SORN_SN(syn_type='GLU'),

                    3: SORN_STDP(eta_stdp='[0.005#0]', prune_stdp=False),#todo warning changed parameter!!!
                    4: SORN_SN(syn_type='GLU'),
                    6: SORN_IP_TI(h_ip='0.04,+-0%', eta_ip='0.005,+-0%', integration_length=10, gap_percent=0),

                    #5: SORN_IP_New(h_ip='[0.1#1],0.05,normal,plot', eta_ip=0.001),
                    #6: SORN_diffuse_IP(h_ip=0.1, eta_ip=0.001, init_avg=0.1),
                    #5: SORN_IP_New(h_ip=0.1, eta_ip=0.001),
                    #5: SORN_IP_New(h_ip='[0.1#1],+-50%', eta_ip='0.001,+-50%'),  #
                    #6: SORN_diffuse_IP(h_ip=0.1, eta_ip=0.001, init_avg=0.1),
                    #6: SORN_diffuse_IP(h_ip='[0.1#1],+-50%', eta_ip='[0.001#2],+-50%', init_avg=0.1),
                    8: SORN_finish(),
                    9: NeuronRecorder(['np.sum(n.x)', 'n.x', 'np.average(n.x)'])
                }))

                if i == 0:
                    SORN_layers_e[-1].add_behaviour(0, NeuronActivator(write_to='input', pattern_groups=[source]))#,source2
                    input_recorders = [SORN_layers_e[-1].add_behaviour(11, NeuronRecorder(['n.input', 'n.pattern_index']))]

                SORN_layers_i.append(NeuronGroup(size=int(0.2 * N_e), behaviour={
                    10: SORN_Input_collect(T_min=0.0, T_max=0.5),
                    11: SORN_finish()
                }))

                ee_syns.append(SynapseGroup(src=SORN_layers_e[-1], dst=SORN_layers_e[-1], connectivity='s_id!=d_id').add_tag('GLU').add_tag('sparse'))
                ie_syns.append(SynapseGroup(src=SORN_layers_e[-1], dst=SORN_layers_i[-1]).add_tag('GLU'))
                ei_syns.append(SynapseGroup(src=SORN_layers_i[-1], dst=SORN_layers_e[-1]).add_tag('GABA'))

                if i > 0:  # connect to previous subsorn
                    ee_forward_syns.append(SynapseGroup(src=SORN_layers_e[-2], dst=SORN_layers_e[-1]).add_tag('GLU').add_tag('sparse'))
                    #ee_backward_syns.append(SynapseGroup(src=SORN_layers_e[-1], dst=SORN_layers_e[-2]).add_tag('GLU').add_tag('sparse'))

                    ie_forward_syns.append(SynapseGroup(src=SORN_layers_e[-2], dst=SORN_layers_i[-1]).add_tag('GLU'))
                    #ie_backward_syns.append(SynapseGroup(src=SORN_layers_e[-1], dst=SORN_layers_i[-2]).add_tag('GLU'))

            SORN_Global = Network(SORN_layers_e + SORN_layers_i, ee_syns + ie_syns + ei_syns + ee_forward_syns + ee_backward_syns + ie_forward_syns + ie_backward_syns, initialize=False)

            SORN_Global.set_marked_variables(ind, info=False)
            SORN_Global.initialize(info=False)

            readout_recorders = [n[9] for n in SORN_layers_e]

            # Step 1. Input with plasticity
            if display: print('Plasticity phase:')
            #SORN_Global.recording_off()
            SORN_Global.simulate_iterations(steps_plastic, 100, measure_block_time=display)
            #SORN_Global.recording_on()

            sm.save_obj('avg', readout_recorders[0]['np.average(n.x)'])
            sm.save_obj('x', readout_recorders[0]['n.x'])

            # Step 2. Input without plasticity: train (with STDP off)
            if display: print('\nReadout training phase:')
            SORN_Global.learning_off()
            SORN_Global.simulate_iterations(steps_readout, 100, measure_block_time=display)

            # Step 3. Train readout layer with logistic regression
            if display: print('\nTraining readout layer...')
            readout_layer = train(readout_recorders, 'n.x', input_recorders, 'n.pattern_index', 0, steps_readout, lag=1)  # steps_plastic, steps_plastic + steps_readout
            SORN_Global.clear_recorder()

            # Step 4. Input without plasticity: test (with STDP and IP off)
            if display: print('\nReadout testing phase:')
            SORN_Global.simulate_iterations(steps_readout, 100, measure_block_time=display)

            # Step 5. Estimate SORN performance
            #if display: print('\nTesting readout layer...')
            #spec_perf = score(readout_layer, readout_recorders, 'n.x', input_recorders, 'n.pattern_index', 0, steps_readout)  # steps_plastic + steps_readout, steps_plastic + steps_readout * 2
            #SORN_Global.clear_recorder()

            # Step 6. Generative SORN with spont_activity (retro feed input)
            if display: print('\nSpontaneous phase:')
            SORN_Global.recording_off()
            SORN_layers_e[0][NeuronActivator].active = False
            spont_output = predict_sequence(readout_layer, SORN_layers_e, 'n.x', steps_spont, SORN_Global, SORN_layers_e[0], source, lag=1)

            if display: print(spont_output)

            # Step 7. Calculate parameters to save
            score_dict = source.get_text_score(spont_output)
            if display: print(score_dict)

            # Step 8. Save
            sm.save_param('spont_output', spont_output)
            sm.save_param_dict(score_dict)


            if display: print('\ndone!')


            #W = ee_syns[0].W.toarray()
            ##W*=W==np.max(W,axis=1)
            #W *= W==np.max(W, axis=0)
            #print(W, W.shape, np.sum(W))
            #ee_syns[0].W=sp.csc_matrix(W)

            #SORN_Global.recording_off()
            #for i in range(40):
            #    if i == 20:
            #        ee_syns[0].W = sp.csc_matrix(ee_syns[0].W.toarray() * (ee_syns[0].W.toarray().transpose() == np.max(ee_syns[0].W.toarray(), axis=1)).transpose())

            #    sm.save_obj('syn{}'.format(i), ee_syns[0].W.toarray())
            #    SORN_Global.simulate_iterations(1000, 100, measure_block_time=display)

            #SORN_Global.simulate_iterations(1000, 100, measure_block_time=display)
            #print('sdf')
            #print((ie_syns[0].W).shape)
            #print((ie_syns[0].W.transpose() == np.max(ie_syns[0].W, axis=1)).shape)
            #print('sdf')

            #print(np.sum(ee_syns[0].W.toarray() * (ee_syns[0].W.toarray().transpose() == np.max(ee_syns[0].W.toarray(), axis=1)).transpose(), axis=1))

            #source2.active = True
            #source.active = False

            #source2.active = False
            #source.active = True

            #ee_syns[0].W = sp.csc_matrix(ee_syns[0].W.toarray() * (ee_syns[0].W.toarray().transpose() == np.max(ee_syns[0].W.toarray(), axis=1)).transpose())
            #SORN_Global.simulate_iterations(steps_plastic, 100, measure_block_time=display)
            #ee_syns[0].W = sp.csc_matrix(ee_syns[0].W.toarray() * (ee_syns[0].W.toarray().transpose() == np.max(ee_syns[0].W.toarray(), axis=1)).transpose())


            #sm.copy_project_files()

            #sm.save_obj('net', SORN_Global)

            #sm.save_obj('net', SORN_Global)
            #sm.save_obj('source', source)
            #sm.save_obj('spec_perf', spec_perf)

            #sm.save_obj('avg', readout_recorders[0]['np.average(n.x)'])

            #plt.plot()
            #plt.show()



        # visualize(SORN_layers_e[0], ee_syns[0])

        #plt.hist(np.array(ee_syns[0].W.toarray())[0], bins=100)
        #plt.ylim([0., 10.0])
        #plt.show()
        #sm.save_obj('source', source)
        #sm.save_obj('ee_n_init', SORN_layers_e[0])
        #sm.save_obj('ee_s_init', ee_syns[0])

        #sm.save_np('ee_weights_init', np.array(ee_syns[0].W.toarray()))

        #clear_recorder()

        #plt.plot(readout_recorders[0]['n.T'])
        #plt.plot(readout_recorders[0]['n.add']*5000, color='black')
        #plt.show()

        #visualize(SORN_layers_e[0], ee_syns[0])

        #sm.save_obj('ee_n', SORN_layers_e[0])
        #sm.save_obj('ee_s', ee_syns[0])
        #sm.save_np('ee_weights', np.array(ee_syns[0].W.toarray()))
        #sm.save_np('T'.format(i, b_key), n.behaviour[b_key])

        #for i, n in enumerate(SORN_layers_e):
        #    for b_key in n.behaviour:
        #        if type(n.behaviour[b_key])==TRENNeuronRecorder_eval:
        #            sm.save_recorder('L{}_{}_'.format(i, b_key), n.behaviour[b_key])


        # Step 9. Plot
        # 10: TRENNeuronRecorder_eval(['n.T'], gapwidth=100)
        # import matplotlib.pyplot as plt
        # plt.plot(SORN_1_e[TRENNeuronRecorder_eval][1]['n.T'])
        # print(SORN_1_e[9]['np.sum(n.x)'])
        # print(SORN_1_e[9]['n.pattern_index'])
        # plt.show()
        if ind != []:
            return (int(score_dict['n_wrong_sentences'])/int(score_dict['n_output']))*(int(score_dict['n_wrong_words'])/int(score_dict['n_words']))

if __name__ == '__main__':
    if False:
        import Exploration.Evolution.Multithreaded_Evolution as Evo
        evolution = Evo.Multithreaded_Evolution(run, 32, thread_count=4, name="100 syn evolution", mutation=0.05, constraints=[])
        evolution.start([[0.005, 0.1, 0.001]])
    else:
        from Exploration.Evolution.Multithreaded_Evolution import *
        run_multiple_times(run, -1)
