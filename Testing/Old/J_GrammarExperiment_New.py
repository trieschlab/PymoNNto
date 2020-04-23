import sys
sys.path.append('../../')

from NetworkBehaviour.Logic.SORN.SORN_advanced import *
from NetworkBehaviour.Input.Text.TextActivator import *
from NetworkCore.Network import *
from NetworkCore.Synapse_Group import *
from NetworkBehaviour.Structure.Structure import *
from Exploration.StorageManager.StorageManager import *

display = False

def run(tag='test', ind=[], par={'N_e':900}):

    sm = StorageManager(tag, random_nr=True, print_msg=display)
    sm.save_param_dict(par)

    source = FDTGrammarActivator_New(tag='grammar_act', output_size=par['N_e'], random_blocks=True)

    e_ng = NeuronGroup(tag='main_exc_group', size=get_squared_dim(par['N_e']),
                       behaviour={
                           1: NeuronActivator(write_to='input', pattern_groups=[source]),
                           2: SORN_init_neuron_vars(iteration_lag=1, init_TH='0.0;0.2'),
                           3: SORN_init_afferent_synapses(transmitter='GLU', density=100, distribution='lognormal(0,[0.89#8])', normalize=True),
                           4: SORN_init_afferent_synapses(transmitter='GABA', density=90, distribution='lognormal(0,[0.8022#9])', normalize=True),

                           12: SORN_slow_syn(transmitter='GLU', strength='[0.138#0]', input_strength=1.0),
                           13: SORN_slow_syn(transmitter='GABA', strength='-[0.1698#1]'),
                           17: SORN_fast_syn(transmitter='GABA', strength='-[0.11045#2]'),
                           20: SORN_input_collect(),

                           21: SORN_STDP(eta_stdp='[0.050399#13]', prune_stdp=False),
                           22: SORN_SN(syn_type='GLU', clip_max=None),
                           23: SORN_IP_TI(h_ip='lognormal_real_mean([0.051296#12], [0.2943#6])', eta_ip='0.00046;+-45.4%', integration_length=9, gap_percent=10, clip_min=-0.001),

                           24: SORN_diffuse_IP(h_dh='IPTI_h_ip', eta_dh='[0.00094567#7]', integration_length=1, gap_percent=10),

                           30: SORN_finish(),

                           100: NeuronRecorder(['np.mean(n.output)', 'np.mean(n.TH)', 'n.output', 'n.TH', 'n.excitation', 'n.inhibition', 'n.input_act'], tag='exc_out_rec'),
                           101: NeuronRecorder(['n.pattern_index'], tag='inp_rec')
                       })

    i_ng = NeuronGroup(tag='main_inh_group', size=get_squared_dim(int(0.2 * par['N_e'])), behaviour={
        2: SORN_init_neuron_vars(iteration_lag=1, init_TH='0.1'),
        3: SORN_init_afferent_synapses(transmitter='GLU', density=450, distribution='lognormal(0,[0.87038#10])', normalize=True),
        4: SORN_init_afferent_synapses(transmitter='GABA', density=40, distribution='lognormal(0,[0.82099#11])', normalize=True),

        11: SORN_slow_syn(transmitter='GABA', strength='-[0.1839#3]'),
        14: SORN_fast_syn(transmitter='GLU', strength='[1.535#4]'),
        15: SORN_fast_syn(transmitter='GABA', strength='-[0.0805#5]'),
        20: SORN_input_collect(),

        30: SORN_finish(),

        100: NeuronRecorder(['np.mean(n.output)', 'np.mean(n.TH)', 'n.output', 'n.TH', 'n.excitation', 'n.inhibition', 'n.input_act'], tag='inh_out_rec')
    })

    ee_syn = SynapseGroup(src=e_ng, dst=e_ng, connectivity='s_id!=d_id').add_tag('GLU')  # .add_tag('sparse')
    ie_syn = SynapseGroup(src=e_ng, dst=i_ng).add_tag('GLU')
    ei_syn = SynapseGroup(src=i_ng, dst=e_ng).add_tag('GABA')
    ii_syn = SynapseGroup(src=i_ng, dst=i_ng).add_tag('GABA')

    SORN_Global = Network([e_ng, i_ng], [ee_syn, ie_syn, ei_syn, ii_syn], initialize=False)

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

