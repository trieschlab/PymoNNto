import sys
sys.path.append('../../')

from NetworkBehaviour.Logic.Example_SORN.SORN_advanced_behaviour import *
from NetworkBehaviour.Input.SORN.TextActivator import *
from NetworkCore.Network import *
from NetworkCore.Synapse_Group import *
from Testing.Common.Grammar_Helper import *
from NetworkBehaviour.Structure.Structure import *
from Exploration.StorageManager.StorageManager import *

display = False
so = True

N_neurons = 900

#source = FDTGrammarActivator_New(tag='grammar_act', random_blocks=True, input_density=15/par['N_e'])#.plot_char_input_statistics()
source = LongDelayGrammar(tag='grammar_act', random_blocks=True, mode=['simple'], input_density=0.015)
#source = Line_Patterns(tag='image_act', group_possibility=1.0, grid_width=30, grid_height=30, center_x=list(range(30)), center_y=30 / 2, degree=90, line_length=60)

SORN = Network()

e_ng = NeuronGroup(net=SORN, tag='PC_Neurons,prediction_source', size=get_squared_dim(int(N_neurons)), behaviour={
    2: SORN_init_neuron_vars(iteration_lag=1, init_TH='0.1;+-100%'),
    3: SORN_init_afferent_synapses(transmitter='GLU', density='13%', distribution='lognormal(0,0.95)', normalize=True, partition_compensation=True),
    4: SORN_init_afferent_synapses(transmitter='GABA', density='45%', distribution='lognormal(0,0.4)', normalize=True),

    12: SORN_slow_syn(transmitter='GLU', strength='0.1383', so=so),
    13: SORN_slow_syn(transmitter='GABA', strength='-0.1698', so=False),
    17: SORN_fast_syn(transmitter='GABA', strength='-0.1', so=False),
    18: SORN_input_collect(),

    19: SORN_Refractory(strength=1, factor='0.5;+-50%'),

    21: SORN_STDP(eta_stdp='0.00015', prune_stdp=False),
    22: SORN_SN(syn_type='GLU', clip_max=None, init_norm_factor=1.0),

    23: SORN_IP_TI(h_ip='lognormal_real_mean(0.04, 0.2944)', eta_ip='0.0006;+-50%', integration_length='15;+-50%', clip_min=None),
    25: SORN_NOX(mp='self.partition_sum(n)', eta_nox='0.5;+-50%'),
    26: SORN_SC_TI(h_sc='lognormal_real_mean(0.015, 0.2944)', eta_sc='0.1;+-50%', integration_length='1'),
    27: SORN_iSTDP(h_ip='same(SCTI, th)', eta_istdp='0.0001'),

    30: SORN_finish()
})

i_ng = NeuronGroup(net=SORN, tag='INH_Neurons', size=get_squared_dim(int(0.2 * N_neurons)), behaviour={
    2: SORN_init_neuron_vars(iteration_lag=1, init_TH='0.1;+-0%'),
    3: SORN_init_afferent_synapses(transmitter='GLU', density='50%', distribution='lognormal(0,0.87038)', normalize=True),  # 450
    4: SORN_init_afferent_synapses(transmitter='GABA', density='20%', distribution='lognormal(0,0.82099)', normalize=True),  # 40

    14: SORN_fast_syn(transmitter='GLU', strength='1.5', so=so),
    15: SORN_fast_syn(transmitter='GABA', strength='-0.08', so=False),
    18: SORN_input_collect(),

    19: SORN_Refractory(strength=1, factor='0.2;0.7'),
    30: SORN_finish()
})

i_ng['structure', 0].stretch_to_equal_size(e_ng)

SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='GLU,e->e', connectivity='(s_id!=d_id)*in_box(10)', partition=True)
SynapseGroup(net=SORN, src=e_ng, dst=i_ng, tag='GLU,e->i', connectivity='in_box(10)', partition=True)
SynapseGroup(net=SORN, src=i_ng, dst=e_ng, tag='GABA,i->e', connectivity='in_box(10)', partition=True)
SynapseGroup(net=SORN, src=i_ng, dst=i_ng, tag='GABA,i->i', connectivity='(s_id!=d_id)*in_box(10)', partition=True)

#i_ng.add_behaviour(10, SORN_external_input(strength=1.0, pattern_groups=[source]))
e_ng.add_behaviour(10, SORN_external_input(strength=1.0, pattern_groups=[source]))

e_ng.color = (0.0, 0.0, 255.0, 255.0)
i_ng.color = (255.0, 0.0, 0.0, 255.0)

SORN.initialize(info=False)

###################################################################################################################

sm = StorageManager('test', random_nr=True, print_msg=display)

#score = train_and_generate_text(SORN, 1500, 500, 200, display=True, stdp_off=True, same_timestep_without_feedback_loop=False, steps_recovery=0, storage_manager=sm)

import Exploration.UI.Network_UI.Network_UI as NUI
NUI.Network_UI(SORN, label='SORN Advanced', storage_manager=sm, group_display_count=2, reduced_layout=True).show()







