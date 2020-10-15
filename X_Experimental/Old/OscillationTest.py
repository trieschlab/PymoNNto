from Testing.Old.SORN_simple_behaviour import *

# 5: SORN_IP_New(h_ip='[0.1#1],0.05,normal,plot', eta_ip=0.001),
# 5: SORN_IP_New(h_ip=0.1, eta_ip=0.001, gap_percent=0),
# 5: SORN_IP_New(h_ip='0.1,+-0%', eta_ip='0.001,+-0%', gap_percent=0),
# 7: SORN_IP_TI(h_ip='0.1,+-10%', eta_ip='0.001,+-10%', integration_length=1000, gap_percent=0),
# 5: SORN_diffuse_IP(h_ip=0.1, eta_ip=0.001, init_avg=0.1, integration_length = 1000),
# 5: SORN_diffuse_IP(h_ip='0.1,+-10%', eta_ip='0.001,+-10%', init_avg=0.1, integration_length=1),


display = True
tag = 'test'#'900N_200S_10diff_100TI_1000TI_10perc_10percgap_rendering'#'reduced_oscillation_tests_default_200_syn_N_e_1000_TI_1000_and_100_and_IP_0perc'

def run(ind=[]):

    for i in range(1):
        for N_e in [900]:
            sm = StorageManager(tag, random_nr=False, print_msg=display)

            source = FDTGrammarActivator_New(output_size=N_e, random_blocks=True)

            e_ng = NeuronGroup(tag='main_exc_group', size=get_squared_dim(N_e), behaviour={ #TRENNeuronDimension(width=30, height=30, depth=1)
                1: NeuronActivator(write_to='input', pattern_groups=[source]),
                2: SORN_Input_collect(T_min=0.0, T_max=0.5, lamb=200, iteration_lag=1, fixed_synapse_count=False),
                3: SORN_STDP(eta_stdp='[0.005#0]', prune_stdp=False),#todo warning changed parameter!!!
                4: SORN_SN(syn_type='GLU'),
                6: SORN_IP_TI(h_ip='0.04,+-0%', eta_ip='0.005,+-0%', integration_length=10, gap_percent=0),
                8: SORN_finish(),
                9: NeuronRecorder(['n.x', 'np.average(n.x)'])
                #11: TRENNeuronRecorder_eval(['n.input', 'n.pattern_index'])
            })

            i_ng = NeuronGroup(tag='main_inh_group', size=int(0.2 * N_e), behaviour={
                10: SORN_Input_collect(T_min=0.0, T_max=0.5),
                11: SORN_finish()
            })

            ee_syn = SynapseGroup(src=e_ng, dst=e_ng, connectivity='s_id!=d_id').add_tag('GLU')#.add_tag('sparse')
            ie_syn = SynapseGroup(src=e_ng, dst=i_ng).add_tag('GLU')
            ei_syn = SynapseGroup(src=i_ng, dst=e_ng).add_tag('GABA')

            SORN_Global = Network([e_ng, i_ng], [ee_syn, ie_syn, ei_syn], initialize=False)#

            SORN_Global.set_marked_variables(ind, info=False)
            SORN_Global.initialize(info=False)

            # for i in range(1000):
            #     SORN_Global.simulate_iterations(100, 100, measure_block_time=display)
            #     sm.save_np('syns{}'.format(i), np.array(ee_syn.W))  # .toarray()

            #SORN_Global.simulate_iterations(100, 100, measure_block_time=display)

            #print(np.array(SORN_Global['main_exc_group']['n.x']).shape)

            import Exploration.Network_UI.Network_UI as SUI
            sui = SUI.Network_UI(SORN_Global, label='SORN UI')
            sui.show()





            '''
            for i in range(10000):
                SORN_Global.simulate_iterations(1, 1, measure_block_time=display)
                image = get_whole_Network_weight_image(e_ng, neuron_src_groups=None, individual_norm=True, exc_weight_attr='W', inh_weight_attr='W', activations=e_ng.x)

                image = upscale(image, 2)

                #image = resize(image, (image.shape[0]*2, image.shape[1]*2), anti_aliasing=False)
                #plt.imshow(image, interpolation="nearest")
                #plt.show()
                #im=np.array([image, np.array(image.shape), np.array(image.shape)])
                sm.save_frame(image*255, 'weights')

            avg = e_ng[9]['np.average(n.x)']
            avg = avg.reshape(-1, 10).mean(axis=-1)
            canvas=sk_plot(avg, image.shape[0], image.shape[1])
            for i in range(10000):
                sm.save_frame(sk_plot(avg, image.shape[0], image.shape[1], v_lines=[i/10], draw_axis=False, draw_data=False, canvas=canvas.copy()), 'skp')

            sm.render_video('skp', True)
            sm.render_video('weights', True)
            '''

            #SORN_Global.simulate_iterations(100000, 100, measure_block_time=display)

            #sm.save_obj('avg', e_ng[9]['np.average(n.x)'])
            #sm.save_obj('x', e_ng[9]['n.x'])

            # sm.save_param('steps_plastic', steps_plastic)





from Exploration.Evolution.Multithreaded_Evolution import *
run_multiple_times(run, -1)

#tag = '900N_200S_10diff_100TI_1000TI_10perc_10percgap'

#from Testing.SORN.SORN_visualization import *
#show_3D_oscillation_plot([tag], 10)
