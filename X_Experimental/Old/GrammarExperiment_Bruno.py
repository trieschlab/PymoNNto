import sys
sys.path.append('../../')

from SORNSim.NetworkBehaviour.Logic.SORN.SORN_advanced import *
from SORNSim.NetworkBehaviour.Input.Text.TextActivator import *
from SORNSim.NetworkCore.Network import *
from SORNSim.NetworkCore.Synapse_Group import *
from SORNSim.NetworkBehaviour.Structure.Structure import *
from SORNSim.Exploration.StorageManager.StorageManager import *

if __name__ == '__main__':
    pass

display = False
def run(tag='bruno', ind=[], par={'N_e':900}):

    sm = StorageManager(tag, random_nr=True, print_msg=display)
    sm.save_param_dict(par)

    source = FDTGrammarActivator_New(tag='grammar_act', output_size=par['N_e'], random_blocks=True, input_density=0.016)

    SORN = Network()

    e_ng = NeuronGroup(net=SORN, tag='main_exc_group,prediction_source', size=get_squared_dim(par['N_e']),
                       behaviour={
                           2: SORN_init_neuron_vars(iteration_lag=1, init_TH='uniform(0.0,0.5)'),
                           3: SORN_init_afferent_synapses(transmitter='GLU', density=10, distribution='uniform(0.0,0.5)', normalize=True),
                           4: SORN_init_afferent_synapses(transmitter='GABA', density='full', distribution='uniform(0.0,0.5)', normalize=True),

                           10: SORN_external_input(write_to='input', pattern_groups=[source]),
                           12: SORN_slow_syn(transmitter='GLU', strength='1.0'),
                           13: SORN_slow_syn(transmitter='GABA', strength='-1.0'),
                           20: SORN_input_collect(),

                           21: SORN_STDP(eta_stdp='0.005', prune_stdp=False),
                           22: SORN_SN(syn_type='GLU', clip_max=None),
                           23: SORN_IP_TI(h_ip='0.1', eta_ip='0.001', integration_length=1, gap_percent=None, clip_min=None),

                           30: SORN_finish(),
                       })

    i_ng = NeuronGroup(net=SORN, tag='main_inh_group', size=get_squared_dim(int(0.2 * par['N_e'])), behaviour={
        2: SORN_init_neuron_vars(iteration_lag=1, init_TH='uniform(0.0,0.5)'),
        #3: SORN_init_afferent_synapses(transmitter='GLU', density=200, normalize=True),
        3: SORN_init_afferent_synapses(transmitter='GLU', density='full', distribution='uniform(0.0,0.5)', normalize=True),

        ##10: SORN_inter_Gamma(transmitter='GLU', strength=0.5, input_strength=1),
        14: SORN_fast_syn(transmitter='GLU', strength='1.0'),
        20: SORN_input_collect(),

        30: SORN_finish(),

        #100: NeuronRecorder(['np.mean(n.output)', 'np.mean(n.TH)', 'n.output', 'n.TH', 'n.excitation', 'n.inhibition', 'n.input_act'], tag='inh_out_rec')
    })

    SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='GLU', connectivity='s_id!=d_id')
    SynapseGroup(net=SORN, src=e_ng, dst=i_ng, tag='GLU')
    SynapseGroup(net=SORN, src=i_ng, dst=e_ng, tag='GABA')

    SORN.set_marked_variables(ind, info=(ind == []))
    SORN.initialize(info=False)

    e_ng.color = get_color(0, 1)
    i_ng.color = get_color(1, 1)

    Network_UI(SORN, label='SORN Bruno', storage_manager=sm, group_display_count=2, reduced_layout=False).show()

    ####################################################
    ####################################################
    ####################################################

    #import Exploration.UI.Network_UI as SUI
    #SUI.Network_UI(SORN_Global, label='SORN UI', exc_group_name='main_exc_group', inh_group_name='main_inh_group', storage_manager=sm).show()

    #return get_evolution_score_words(SORN_Global, 20000, 5000, 2000, display=True, stdp_off=True, storage_manager=sm)
    #return get_evolution_score(SORN_Global, 5000, 3000, 0.2, e_ng, i_ng)#0.04
    #return get_evolution_score_simple(SORN_Global, 5000, 4000, e_ng)


if __name__ == '__main__':
    run('bruno', [], par={'N_e': 900})



