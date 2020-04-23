import sys
sys.path.append('../../')

from NetworkBehaviour.Structure.Structure import *
from NetworkCore.Network import *
from NetworkCore.Synapse_Group import *
from NetworkBehaviour.Logic.Example_SORN.SORN_advanced_behaviour import *
from NetworkBehaviour.Input.Text.TextActivator import *
from Exploration.UI.Network_UI.Network_UI import *
from Exploration.UI.Network_UI.Tabs.sidebar_grammar_module import *

N_neurons = 900

source = FDTGrammarActivator_New(tag='grammar_act', output_size=N_neurons, random_blocks=True)

SORN = Network()

e_ng = NeuronGroup(net=SORN, tag='main_exc_group,prediction_source', size=get_squared_dim(N_neurons), behaviour={

    2: SORN_init_neuron_vars(init_TH='uniform(0.0,0.5)'),
    3: SORN_init_afferent_synapses(transmitter='GLU', density=10, distribution='uniform(0.0,0.5)', normalize=True),
    4: SORN_init_afferent_synapses(transmitter='GABA', density='full', distribution='uniform(0.0,0.5)', normalize=True),

    9: SORN_external_input(strength=1.0, pattern_groups=[source]),

    12: SORN_slow_syn(transmitter='GLU', strength='1.0'),
    13: SORN_slow_syn(transmitter='GABA', strength='-1.0'),
    20: SORN_input_collect(),

    21: SORN_STDP(eta_stdp='0.005', prune_stdp=False),
    22: SORN_SN(syn_type='GLU', clip_max=None),
    23: SORN_IP_TI(h_ip='0.1', eta_ip='0.001', integration_length=1, gap_percent=None, clip_min=None),
    30: SORN_finish()
})

i_ng = NeuronGroup(net=SORN, tag='main_inh_group', size=get_squared_dim(int(0.2 * N_neurons)), behaviour={
    2: SORN_init_neuron_vars(init_TH='uniform(0.0,0.5)'),
    3: SORN_init_afferent_synapses(transmitter='GLU', density='full', distribution='uniform(0.0,0.5)', normalize=True),

    14: SORN_fast_syn(transmitter='GLU', strength='1.0'),
    20: SORN_input_collect(),

    30: SORN_finish()
})

SynapseGroup(net=SORN, src=e_ng, dst=e_ng, connectivity='s_id!=d_id', tag='GLU')
SynapseGroup(net=SORN, src=e_ng, dst=i_ng, tag='GLU')
SynapseGroup(net=SORN, src=i_ng, dst=e_ng, tag='GABA')

SORN.initialize(info=False)

e_ng.color = (0, 0, 255, 255)
i_ng.color = (255, 0, 0, 255)

#train_and_generate_text(SORN, steps_plastic=15000, steps_train=5000, steps_spont=2000, storage_manager=None)


Network_UI(SORN, label='SORN Simple', group_display_count=2).show()
