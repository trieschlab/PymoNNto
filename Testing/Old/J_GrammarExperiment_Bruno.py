import sys
sys.path.append('../../')

from NetworkBehaviour.Logic.SORN.SORN_advanced import *
from NetworkBehaviour.Input.Text.TextActivator import *
from NetworkCore.Network import *
from NetworkCore.Synapse_Group import *
from NetworkBehaviour.Structure.Structure import *
from Exploration.StorageManager.StorageManager import *

display = False
def run(tag='bruno', ind=[], par={'N_e':900}):

    sm = StorageManager(tag, random_nr=True, print_msg=display)
    sm.save_param_dict(par)

    source = FDTGrammarActivator_New(tag='grammar_act', output_size=par['N_e'], random_blocks=True)

    e_ng = NeuronGroup(tag='main_exc_group', size=get_squared_dim(par['N_e']),
                       behaviour={
                           1: NeuronActivator(write_to='input', pattern_groups=[source]),
                           2: SORN_init_neuron_vars(iteration_lag=1, init_TH='uniform(0.0,0.5)'),
                           3: SORN_init_afferent_synapses(transmitter='GLU', density=10, distribution='uniform(0.0,0.5)', normalize=True),
                           4: SORN_init_afferent_synapses(transmitter='GABA', density='full', distribution='uniform(0.0,0.5)', normalize=True),

                           12: SORN_slow_syn(transmitter='GLU', strength='1.0', input_strength=1.0),
                           13: SORN_slow_syn(transmitter='GABA', strength='-1.0'),
                           20: SORN_input_collect(),

                           21: SORN_STDP(eta_stdp='0.005', prune_stdp=False),
                           22: SORN_SN(syn_type='GLU', clip_max=None),
                           23: SORN_IP_TI(h_ip='0.1', eta_ip='0.001', integration_length=1, gap_percent=None, clip_min=None),

                           30: SORN_finish(),

                           100: NeuronRecorder(['np.mean(n.output)', 'np.mean(n.TH)', 'n.output', 'n.TH', 'n.excitation', 'n.inhibition', 'n.input_act'], tag='exc_out_rec'),
                           101: NeuronRecorder(['n.pattern_index'], tag='inp_rec')
                       })

    i_ng = NeuronGroup(tag='main_inh_group', size=get_squared_dim(int(0.2 * par['N_e'])), behaviour={
        2: SORN_init_neuron_vars(iteration_lag=1, init_TH='uniform(0.0,0.5)'),
        3: SORN_init_afferent_synapses(transmitter='GLU', density='full', distribution='uniform(0.0,0.5)', normalize=True),

        14: SORN_fast_syn(transmitter='GLU', strength='1.0'),
        20: SORN_input_collect(),

        30: SORN_finish(),

        100: NeuronRecorder(['np.mean(n.output)', 'np.mean(n.TH)', 'n.output', 'n.TH', 'n.excitation', 'n.inhibition', 'n.input_act'], tag='inh_out_rec')
    })

    ee_syn = SynapseGroup(src=e_ng, dst=e_ng, connectivity='s_id!=d_id').add_tag('GLU')  # .add_tag('sparse')
    ie_syn = SynapseGroup(src=e_ng, dst=i_ng).add_tag('GLU')
    ei_syn = SynapseGroup(src=i_ng, dst=e_ng).add_tag('GABA')

    SORN_Global = Network([e_ng, i_ng], [ee_syn, ie_syn, ei_syn], initialize=False)

    SORN_Global.set_marked_variables(ind, info=(ind == []))
    SORN_Global.initialize(info=False)

    ####################################################
    ####################################################
    ####################################################

    import Exploration.UI.Network_UI.Network_UI as SUI
    SUI.Network_UI(SORN_Global, label='SORN UI', exc_group_name='main_exc_group', inh_group_name='main_inh_group', storage_manager=sm).show()

    return get_evolution_score_words(SORN_Global, 20000, 5000, 2000, display=True, stdp_off=True, storage_manager=sm)


if __name__ == '__main__':
    run()

