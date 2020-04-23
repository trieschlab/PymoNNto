import sys
sys.path.append('../../')

from NetworkBehaviour.Logic.Example_SORN.SORN_advanced_behaviour import *
from NetworkBehaviour.Input.Text.TextActivator import *
from NetworkCore.Network import *
from NetworkCore.Synapse_Group import *
from NetworkBehaviour.Structure.Structure import *
from Exploration.StorageManager.StorageManager import *
from Exploration.UI.Network_UI.Network_UI import *

so = True

n_Neurons = 900

#source = FDTGrammarActivator_New(tag='grammar_act', random_blocks=True, input_density=0.015)#.plot_char_input_statistics()#output_size=par['N_e']#15
source = LongDelayGrammar(tag='grammar_act', random_blocks=True, mode=['simple'], input_density=0.015)
#source = Line_Patterns(tag='image_act', group_possibility=1.0, grid_width=30, grid_height=30, center_x=list(range(30)), center_y=30 / 2, degree=90, line_length=60)
#source = Line_Patterns(tag='image_act', group_possibility=1.0, grid_width=30, grid_height=30, center_x=list(range(30)), center_y=30 / 2, degree=90, line_length=60)

SORN = Network()

PC = NeuronGroup(net=SORN, tag='Pyramidal,prediction_source', size=get_squared_dim(int(n_Neurons)), behaviour={
    2: SORN_init_neuron_vars(nit_TH='0.1;+-100%'),
    3: SORN_init_afferent_synapses(transmitter='GLU', density='50%', distribution='uniform(0.1,0.11)', normalize=True, partition_compensation=True), #lognormal(0,0.6)
    4: SORN_init_afferent_synapses(transmitter='GABA_Dendrite', density='30%', distribution='uniform(0.1,0.11)', normalize=True),
    5: SORN_init_afferent_synapses(transmitter='GABA_Soma', density='30%', distribution='uniform(0.1,0.11)', normalize=True),
    6: SORN_init_afferent_synapses(transmitter='GABA_AIS', density='30%', distribution='uniform(0.1,0.11)', normalize=True),

    12: SORN_slow_syn(transmitter='GLU', strength='0.1383', so=so),
    13: SORN_slow_syn(transmitter='GABA_Dendrite', strength='-0.1', so=False),
    14: SORN_slow_input_collect(),

    17: SORN_fast_syn(transmitter='GABA_Soma', strength='-0.1', so=False),
    17.1: SORN_fast_syn(transmitter='GABA_AIS', strength='-0.1', so=False),
    19: SORN_input_collect(),

    20: SORN_Refractory(factor='0.5;+-50%'),
    21: SORN_STDP_new(eta_stdp='0.0015', prune_stdp=False, excitation_punishment=0.0),#0.1#todo: test!!!
    22: SORN_SN(syn_type='GLU', clip_max=None, init_norm_factor=1.0),

    23: SORN_IP_TI(mp='n.output_new/2.0+n.output_new_temp/2.0', h_ip='lognormal_real_mean(0.04, 0.2944)', eta_ip='0.0006;+-50%', integration_length='15;+-50%', clip_min=None),
    25: SORN_NOX(mp='self.partition_sum(n)', eta_nox='0.5;+-50%', h_dh=0.0),#0.9#0.3
    26: SORN_SC_TI(h_sc='lognormal_real_mean(0.015, 0.2944)', eta_sc='0.1;+-50%', integration_length='1'),

    30: SORN_finish()
})


MT_SOM = NeuronGroup(net=SORN, tag='Martinotti_(SOM)', size=get_squared_dim(int(0.07 * n_Neurons)), behaviour={
    2: SORN_init_neuron_vars(init_TH='0.1;+-0%'),
    3: SORN_init_afferent_synapses(transmitter='GLU', density='50%', distribution='lognormal(0,0.87038)', normalize=True),

    10: SORN_slow_syn(transmitter='GLU', strength='0.6', so=so),  # 1.5353

    19: SORN_input_collect(),
    30: SORN_finish()
})

BA_PV = NeuronGroup(net=SORN, tag='Basket_(PV)', size=get_squared_dim(int(0.07 * n_Neurons)), behaviour={
    2: SORN_init_neuron_vars(iteration_lag=1, init_TH='0.1;+-0%'),
    3: SORN_init_afferent_synapses(transmitter='GLU', density='50%', distribution='lognormal(0,0.87038)', normalize=True),

    10: SORN_slow_syn(transmitter='GLU', strength='0.6', so=so),  # 1.5353

    19: SORN_input_collect(),
    30: SORN_finish()
})

CH_PV = NeuronGroup(net=SORN, tag='Chandelier_(PV)', size=get_squared_dim(int(0.07 * n_Neurons)), behaviour={
    2: SORN_init_neuron_vars(iteration_lag=1, init_TH='0.1;+-0%'),
    3: SORN_init_afferent_synapses(transmitter='GLU', density='50%', distribution='lognormal(0,0.87038)', normalize=True),

    14: SORN_fast_syn(transmitter='GLU', strength='0.4', so=so),

    19: SORN_input_collect(),
    30: SORN_finish()
})

MT_SOM['structure', 0].stretch_to_equal_size(PC)
BA_PV['structure', 0].stretch_to_equal_size(PC)
CH_PV['structure', 0].stretch_to_equal_size(PC)

SynapseGroup(net=SORN, src=PC, dst=PC, tag='GLU,PC->PC', connectivity='(s_id!=d_id)*in_box(10)', partition=True)
SynapseGroup(net=SORN, src=PC, dst=MT_SOM, tag='GLU,PC->MT', connectivity='in_box(2)', partition=True)
SynapseGroup(net=SORN, src=PC, dst=BA_PV, tag='GLU,PC->BA', connectivity='in_box(2)', partition=True)
SynapseGroup(net=SORN, src=PC, dst=CH_PV, tag='GLU,PC->CH', connectivity='in_box(2)', partition=True)

SynapseGroup(net=SORN, src=MT_SOM, dst=PC, tag='GABA_Dendrite,MT->PC', connectivity='in_box(10)', partition=True)
SynapseGroup(net=SORN, src=BA_PV, dst=PC, tag='GABA_Soma,BA->PC', connectivity='in_box(10)', partition=True)
SynapseGroup(net=SORN, src=CH_PV, dst=PC, tag='GABA_AIS,CH->PC', connectivity='in_box(10)', partition=True)

PC.add_behaviour(9, SORN_external_input(strength=1.0, pattern_groups=[source]))

PC.color = (0.0, 0.0, 255.0, 255.0)
MT_SOM.color = (255.0, 0.0, 0.0, 255.0)
BA_PV.color = (255.0, 150.0, 0.0, 255.0)
CH_PV.color = (255.0, 80.0, 0.0, 255.0)

SORN.initialize(info=False)

###################################################################################################################

sm = StorageManager('test', random_nr=True)

#train_and_generate_text(SORN, 15000, 5000, 2000, stdp_off=True, same_timestep_without_feedback_loop=False, steps_recovery=0, storage_manager=sm)


Network_UI(SORN, label='SORN UI PC PV SOM', storage_manager=sm, group_display_count=4).show()


