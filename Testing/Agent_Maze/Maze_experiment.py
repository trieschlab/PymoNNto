import sys

sys.path.append('../../')

from NetworkBehaviour.Logic.SORN.SORN_advanced_buffer import *
from NetworkCore.Network import *
from NetworkCore.Synapse_Group import *
from Exploration.StorageManager.StorageManager import *

from Testing.Agent_Maze.Maze import *

if __name__ == '__main__':
    pass


def run(attrs={'name': 'maze', 'ind': [], 'N_e': 900, 'TS': [1], 'ff': True, 'fb': True, 'plastic': 15000}):
    so = True

    print_info = attrs.get('print', True)

    if print_info:
        print(attrs)

    sm = StorageManager(attrs, random_nr=True, print_msg=print_info)
    sm.save_param_dict(attrs)

    #source = LongDelayGrammar(tag='grammar_act', output_size=attrs['N_e'], random_blocks=True, mode=['simple'], input_density=0.01)
    maze = Maze(level='default')


    SORN = Network()#behaviour={maze.get_network_behaviour()}

    SORN.maze = maze

    for layer, timescale in enumerate(attrs['TS']):

        e_location = NeuronGroup(net=SORN, tag='E_location_{}'.format(timescale), size=maze.get_location_neuron_dimension(), behaviour={
                2: SORN_init_neuron_vars(timescale=timescale),
                3: SORN_init_afferent_synapses(transmitter='GLU', density='full', distribution='uniform(0.1,0.11)', normalize=True, partition_compensation=True),  # 0.89 uniform(0.1,0.11)uniform(0,[0.95#0])
                4: SORN_init_afferent_synapses(transmitter='GABA', density='full', distribution='uniform(0.1,0.11)', normalize=True),  # 0.80222 uniform(0.1,0.11) lognormal(0,[0.4#1])

                9:maze.get_location_neuron_behaviour(),###############

                12: SORN_slow_syn(transmitter='GLU', strength='[0.1383#2]', so=so),
                13: SORN_slow_syn(transmitter='GABA', strength='-[0.1698#3]', so=False),
                17: SORN_fast_syn(transmitter='GABA', strength='-[0.1#4]', so=False),  # 0.11045
                18: SORN_generate_output(init_TH='0.1;+-100%'),
                19: SORN_buffer_variables(),

                20: SORN_Refractory(factor='0.5;+-50%'),
                21: SORN_STDP(eta_stdp='[0.0015#5]', weight_attr='W_temp', STDP_F={-5:0.2, -4:0.4, -3:0.6, -2:0.8, -1: 1}),
                22: SORN_temporal_synapses(syn_type='GLU', behaviour_norm_factor=1.0),
                #22: SORN_SN(syn_type='GLU', clip_max=None, behaviour_norm_factor=1.0),


                23: SORN_IP_TI(h_ip='lognormal_real_mean([0.004#6], [0.2944#7])', eta_ip='[0.0006#8];+-50%', integration_length='[15#18];+-50%', clip_min=None),
                25: SORN_NOX(mp='self.partition_sum(n)', eta_nox='[0.5#9];+-50%'),
                26: SORN_SC_TI(h_sc='lognormal_real_mean([0.015#10], [0.2944#11])', eta_sc='[0.1#12];+-50%',
                               integration_length='1'),  # 60;+-50% #0.05
                27: SORN_iSTDP(h_ip='same(SCTI, th)', eta_istdp='[0.0001#13]'),

                #29: SORN_dopamine(),
            })

        i_location = NeuronGroup(net=SORN, tag='I_location{}'.format(timescale), size=maze.get_inhibitory_location_neuron_dimension(), behaviour={
                2: SORN_init_neuron_vars(timescale=timescale),
                3: SORN_init_afferent_synapses(transmitter='GLU', density='50%', distribution='uniform(0.1,0.11)', normalize=True),#lognormal(0,[0.87038#14])
                4: SORN_init_afferent_synapses(transmitter='GABA', density='20%', distribution='uniform(0.1,0.11)', normalize=True),#lognormal(0,[0.82099#15])

                11: SORN_slow_syn(transmitter='GABA', strength='-[0.1838#16]', so=so),
                14: SORN_fast_syn(transmitter='GLU', strength='[1.5#16]', so=so),  # 1.5353
                15: SORN_fast_syn(transmitter='GABA', strength='-[0.08#17]', so=False),  # 0.08
                18: SORN_generate_output(init_TH='0.1;+-0%'),
                19: SORN_buffer_variables(),

                20: SORN_Refractory(factor='0.2;0.7'),
            })

        '''
        e_vision = NeuronGroup(net=SORN, tag='E_vision_{}'.format(timescale), size=maze.get_vision_neuron_dimension(), behaviour={
                2: SORN_init_neuron_vars(timescale=timescale),
                3: SORN_init_afferent_synapses(transmitter='GLU', density='full', distribution='lognormal(0,[0.95#0])', normalize=True, partition_compensation=True),  # 0.89 uniform(0.1,0.11)
                4: SORN_init_afferent_synapses(transmitter='GABA', density='45%', distribution='lognormal(0,[0.4#1])', normalize=True),  # 0.80222 uniform(0.1,0.11)

                9: maze.get_vision_neuron_behaviour(),

                12: SORN_slow_syn(transmitter='GLU', strength='[0.1383#2]', so=so),
                13: SORN_slow_syn(transmitter='GABA', strength='-[0.1698#3]', so=False),
                17: SORN_fast_syn(transmitter='GABA', strength='-[0.1#4]', so=False),  # 0.11045
                18: SORN_generate_output(init_TH='0.01'),
                19: SORN_buffer_variables(),

                #20: SORN_Refractory(factor='0.5;+-50%'),
                #21: SORN_STDP(eta_stdp='[0.00015#5]'),
                #22: SORN_SN(syn_type='GLU', clip_max=None, behaviour_norm_factor=5.0),

                #23: SORN_IP_TI(h_ip='0.04', eta_ip='0.001', integration_length='[15#18];+-50%', clip_min=None),
                #25: SORN_NOX(mp='self.partition_sum(n)', eta_nox='[0.5#9];+-50%'),
                #26: SORN_SC_TI(h_sc='lognormal_real_mean([0.015#10], [0.2944#11])', eta_sc='[0.1#12];+-50%',integration_length='1'),  # 60;+-50% #0.05
                #27: SORN_iSTDP(h_ip='same(SCTI, th)', eta_istdp='[0.0001#13]')

            })
        '''

        e_action = NeuronGroup(net=SORN, tag='E_action_{}'.format(timescale), size=maze.get_action_neuron_dimension(), behaviour={
                2: SORN_init_neuron_vars(timescale=timescale),
                3: SORN_init_afferent_synapses(transmitter='GLU', density='full', distribution='uniform(0.1,0.11)', normalize=True, partition_compensation=True),  # 0.89 lognormal(0,[0.5#0])

                12: SORN_slow_syn(transmitter='GLU', strength='[0.1383#2]', so=so),
                13: SORN_slow_syn(transmitter='GABA', strength='-[0.1698#3]', so=False),
                17: SORN_fast_syn(transmitter='GABA', strength='-[0.1#4]', so=False),  # 0.11045
                18: SORN_generate_output(init_TH='0.01'),
                19: SORN_buffer_variables(),

                20: SORN_Refractory(factor='0.7;+-50%'),
                21: SORN_STDP(eta_stdp='[0.0015#5]', STDP_F={-1: 1, 1:0}, weight_attr='W_temp'),#bigger #todo!!!!
                #22: SORN_SN(syn_type='GLU', clip_max=None, behaviour_norm_factor=5.0),
                22: SORN_temporal_synapses(syn_type='GLU', behaviour_norm_factor=5.0),

                23: SORN_IP_TI(h_ip='0.04', eta_ip='0.001', integration_length='[15#18];+-50%', clip_min=None),
                #25: SORN_NOX(mp='self.partition_sum(n)', eta_nox='[0.5#9];+-50%'),
                #26: SORN_SC_TI(h_sc='lognormal_real_mean([0.015#10], [0.2944#11])', eta_sc='[0.1#12];+-50%',integration_length='1'),  # 60;+-50% #0.05
                #27: SORN_iSTDP(h_ip='same(SCTI, th)', eta_istdp='[0.0001#13]')

                29: SORN_dopamine(),

                30: maze.get_action_neuron_behaviour()
            })

        '''
        e_reward = NeuronGroup(net=SORN, tag='E_reward_{}'.format(timescale), size=maze.get_reward_neuron_dimension(), behaviour={
                2: SORN_init_neuron_vars(timescale=timescale),
                3: SORN_init_afferent_synapses(transmitter='GLU', density='full', distribution='lognormal(0,[0.95#0])', normalize=True, partition_compensation=True),

                9: maze.get_reward_neuron_behaviour(),

                12: SORN_slow_syn(transmitter='GLU', strength='[0.1383#2]', so=so),
                18: SORN_generate_output(init_TH='0.01'),
                19: SORN_buffer_variables(),

                #20: SORN_Refractory(factor='0.5;+-50%'),
                21: SORN_STDP(eta_stdp='[0.00015#5]'),
                22: SORN_SN(syn_type='GLU', clip_max=None, behaviour_norm_factor=0.1),

                #23: SORN_IP_TI(h_ip='0.04', eta_ip='0.001', integration_length='[15#18];+-50%', clip_min=None),
                #25: SORN_NOX(mp='self.partition_sum(n)', eta_nox='[0.5#9];+-50%'),
                #26: SORN_SC_TI(h_sc='lognormal_real_mean([0.015#10], [0.2944#11])', eta_sc='[0.1#12];+-50%',integration_length='1'),  # 60;+-50% #0.05
                #27: SORN_iSTDP(h_ip='same(SCTI, th)', eta_istdp='[0.0001#13]')
            })
        '''

        e_punishment = NeuronGroup(net=SORN, tag='E_punishment_{}'.format(timescale), size=maze.get_punishment_neuron_dimension(), behaviour={
                2: SORN_init_neuron_vars(timescale=timescale),
                3: SORN_init_afferent_synapses(transmitter='GLU', density='full', distribution='lognormal(0,[0.95#0])', normalize=True, partition_compensation=True),

                9: maze.get_punishment_neuron_behaviour(),

                12: SORN_slow_syn(transmitter='GLU', strength='[0.1383#2]', so=so),
                18: SORN_generate_output(init_TH='0.01'),
                19: SORN_buffer_variables(),

                #20: SORN_Refractory(factor='0.5;+-50%'),
                21: SORN_STDP(eta_stdp='[0.00015#5]'), #todo!!!!
                22: SORN_SN(syn_type='GLU', clip_max=None, behaviour_norm_factor=0.1),

                #23: SORN_IP_TI(h_ip='0.04', eta_ip='0.001', integration_length='[15#18];+-50%', clip_min=None),
                #25: SORN_NOX(mp='self.partition_sum(n)', eta_nox='[0.5#9];+-50%'),
                #26: SORN_SC_TI(h_sc='lognormal_real_mean([0.015#10], [0.2944#11])', eta_sc='[0.1#12];+-50%',integration_length='1'),  # 60;+-50% #0.05
                #27: SORN_iSTDP(h_ip='same(SCTI, th)', eta_istdp='[0.0001#13]')
            })

        i_location['structure', 0].stretch_to_equal_size(e_location)

        SynapseGroup(net=SORN, src=e_location, dst=e_location, tag='GLU,GLU_same', connectivity='(s_id!=d_id)*in_box(10)', partition=True)
        SynapseGroup(net=SORN, src=e_location, dst=i_location, tag='GLU', connectivity='in_box(10)', partition=True)
        SynapseGroup(net=SORN, src=i_location, dst=e_location, tag='GABA', connectivity='in_box(10)', partition=True)
        SynapseGroup(net=SORN, src=i_location, dst=i_location, tag='GABA', connectivity='(s_id!=d_id)*in_box(10)', partition=True)

        #SynapseGroup(net=SORN, src=e_vision, dst=e_location, tag='GLU', partition=True)
        SynapseGroup(net=SORN, src=e_location, dst=e_action, tag='GLU', partition=True)

        #SynapseGroup(net=SORN, src=e_location, dst=e_reward, tag='GLU', partition=True)
        #SynapseGroup(net=SORN, src=e_reward, dst=e_location, tag='DOP+', partition=True)
        #SynapseGroup(net=SORN, src=e_reward, dst=e_action, tag='DOP+', partition=True)

        SynapseGroup(net=SORN, src=e_location, dst=e_punishment, tag='GLU', partition=True)
        SynapseGroup(net=SORN, src=e_punishment, dst=e_location, tag='DOP-', partition=True)
        SynapseGroup(net=SORN, src=e_punishment, dst=e_action, tag='DOP-', partition=True)

        if __name__ == '__main__' and attrs.get('UI', False):
            e_location.color = (0, 0, 255, 255)
            i_location.color = (255, 0, 0, 255)
            e_action.color = (255, 255, 0, 255)
            #e_vision.color = (0, 255, 255, 255)
            #e_reward.color = (100, 255, 100, 255)
            e_punishment.color = (255, 100, 100, 255)

    SORN.set_marked_variables(attrs['ind'], info=print_info, storage_manager=sm)
    SORN.initialize(info=False)

    ###################################################################################################################

    if __name__ == '__main__' and attrs.get('UI', False):
        default_modules.insert(0, maze_tab())
        Network_UI(SORN, label='SORN UI default setup', storage_manager=sm, group_display_count=4, reduced_layout=True).show()


    return 0


if __name__ == '__main__':
    ind = []
    print('score', run(attrs={'name': 'test', 'ind': ind, 'N_e': 900, 'TS': [1], 'UI': True}))
