import sys

sys.path.append('../../')

from SORNSim.NetworkCore.Network import *
from SORNSim.NetworkCore.Synapse_Group import *
from Testing.Common.Grammar_Helper import *
from SORNSim.NetworkBehaviour.Logic.SORN.SORN_experimental import *
from SORNSim.NetworkBehaviour.Logic.SORN.SORN_WTA import *
from SORNSim.NetworkBehaviour.Input.Text.TextActivator import *
from SORNSim.NetworkBehaviour.Structure.Structure import *
from SORNSim.Exploration.StorageManager.StorageManager import *


if __name__ == '__main__':
    pass

class SORN_K_random_input(Behaviour):

    def set_variables(self, neurons):
        self.K = int(neurons.size*0.04)
        neurons.output=neurons.get_neuron_vec()

    def new_iteration(self, neurons):

        if neurons.iteration % 10 == 0:
            rnd=neurons.get_random_neuron_vec()*0.0001
            ind = np.argpartition(rnd, -self.K)[-self.K:]
            neurons.output.fill(0)
            neurons.output[ind] = 1

            neurons.activity=rnd


class SORN_generate_output_K_WTA_partitioned_dec_k(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('K_WTA_partitioned')

        self.filter_temporal_output = self.get_init_attr('filter_temporal_output', False, neurons)

        neurons.output = neurons.get_neuron_vec()

        self.K = self.get_init_attr('K', 0.1, neurons)#only accepts values between 0 and 1

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):

            mul = (4 - (neurons.iteration % 10))

            if mul < 1:
                mul = 1

            k_mul = self.K * mul

            print(k_mul)

            for s in neurons.afferent_synapses['GLU']:
                K = s.dst.size * k_mul

                #for non integer K
                K_floor = int(np.floor(K))

                if np.random.rand() < (K-K_floor):
                    K = K_floor+1
                else:
                    K = K_floor

                act = s.dst.activity

                if self.filter_temporal_output:
                    act = s.dst.activity*s.dst.output

                ind = np.argpartition(act, -K)[-K:]
                act_mat = np.zeros(s.dst.size)
                act_mat[ind] = 1
                s.dst.output *= 0
                #s.dst.output[ind] += 1
                s.dst.output += act_mat

                #s.dst._temp_act_sum += np.mean(s.src.output)

class SORN_init_neuron_vars_no_reset(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('init_neuron_vars')

        neurons.activity = neurons.get_neuron_vec()
        neurons.excitation = neurons.get_neuron_vec()
        neurons.inhibition = neurons.get_neuron_vec()
        neurons.input_act = neurons.get_neuron_vec()

        #neurons.slow_act=neurons.get_neuron_vec()

        neurons.timescale = self.get_init_attr('timescale', 1)

    def new_iteration(self, neurons):
        if first_cycle_step(neurons):
            neurons.excitation.fill(0)# *= 0
            neurons.inhibition.fill(0)# *= 0
            neurons.input_act.fill(0)# *= 0

        #neurons.buffer_timescale_sum_dict={}

            #neurons.slow_act *= 0

def run(attrs={'name': 'KWTA', 'ind': [], 'N_e': 900, 'TS': [1], 'ff': True, 'fb': True, 'plastic': 15000}):
    so = True

    print_info = attrs.get('print', True)

    if print_info:
        print(attrs)

    sm = StorageManager(attrs['name'], random_nr=True, print_msg=print_info)
    sm.save_param_dict(attrs)

    source = FewSentencesGrammar(tag='grammar_act', output_size=attrs['N_e'], random_blocks=True, input_density=0.015)
    #source = SingleWordGrammar(tag='grammar_act', output_size=attrs['N_e'], random_blocks=True, input_density=0.015)
    #source = FewLongSentencesGrammar(tag='grammar_act', output_size=attrs['N_e'], random_blocks=True, input_density=0.015)
    #source.plot_char_frequency_histogram(20)

    SORN = Network()

    e_ng = NeuronGroup(net=SORN, tag='PC_{},prediction_source'.format(1), size=get_squared_dim(attrs['N_e']), behaviour={
                2: SORN_init_neuron_vars_no_reset(timescale=1),
                #3: SORN_init_afferent_synapses(transmitter='GLU', density='90%', distribution='uniform(0.5,1.0)', normalize=True),
                5: SORN_init_afferent_synapses(transmitter='GLU_cluster', density='90%', distribution='uniform(0.9,1.0)', normalize=True),

                #10.0: SORN_slow_syn(transmitter='GLU', strength='1.0', so=so),
                10.1: SORN_IP_WTA_apply(),
                10.15: WTA_refrac_apply(strengthfactor=0.1),
                #10.2: SORN_generate_output_K_WTA_partitioned(K='0.24'),

                8.3: SORN_slow_syn_simple(transmitter='GLU_cluster', strength='1.0'),
                8.4: SORN_generate_output_K_WTA_partitioned(K='0.04', filter_temporal_output=False),

                #10.5: SORN_slow_syn_simple(transmitter='GLU_cluster', strength='1.0'),
                #10.6: SORN_generate_output_K_WTA_partitioned(K='0.08', filter_temporal_output=True),

                #10.7: SORN_slow_syn_simple(transmitter='GLU_cluster', strength='1.0'),
                #10.8: SORN_generate_output_K_WTA_partitioned(K='0.04', filter_temporal_output=True),

                15: SORN_buffer_variables(random_temporal_output_shift=False),

                18: WTA_refrac(),
                20: SORN_IP_WTA(h_ip='lognormal_real_mean(0.04, 0.2944)', eta_ip='0.007', clip_min=None),
                #21.1: SORN_STDP(transmitter='GLU', eta_stdp='0.00015', STDP_F={-1: 1, 1: -1}),#, 0: 1 #[0.00015#7]
                21.2: SORN_STDP(transmitter='GLU_cluster', eta_stdp='0.00015', STDP_F={0: 0.5}),  #[0.00015#7]
                #22: SORN_SN(syn_type='GLU', behaviour_norm_factor=1.0),
                23: SORN_SN(syn_type='GLU_cluster', behaviour_norm_factor=0.1)
            })

    SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='syn,GLU', connectivity='(s_id!=d_id)*in_box(10)')#, partition=True)
    #SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='syn,GLU_cluster', connectivity='(s_id!=d_id)*in_box(10)', partition=True)

    #SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='GLU', connectivity='(s_id!=d_id)*in_box(10)')#, partition=True)
    SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='GLU_cluster', connectivity='(s_id!=d_id)*((sy<0)*(dy<0)*(sx<0)*(dx<0)+(sy>=0)*(dy>=0)*(sx>=0)*(dx>=0)+(sy<0)*(dy<0)*(sx>=0)*(dx>=0)+(sy>=0)*(dy>=0)*(sx<0)*(dx<0))')

    '''
    '(s_id!=d_id)*('+
                                                                               '(s_id>=35*0)*(d_id>=35*0)*(s_id<35*1)*(d_id<35*1)+' +
                                                                               '(s_id>=35*1)*(d_id>=35*1)*(s_id<35*2)*(d_id<35*2)+' +
                                                                               '(s_id>=35*2)*(d_id>=35*2)*(s_id<35*3)*(d_id<35*3)+' +
                                                                               '(s_id>=35*3)*(d_id>=35*3)*(s_id<35*4)*(d_id<35*4)+' +
                                                                               '(s_id>=35*4)*(d_id>=35*4)*(s_id<35*5)*(d_id<35*5)+' +
                                                                               '(s_id>=35*5)*(d_id>=35*5)*(s_id<35*6)*(d_id<35*6)+' +
                                                                               '(s_id>=35*6)*(d_id>=35*6)*(s_id<35*7)*(d_id<35*7)+' +
                                                                               '(s_id>=35*7)*(d_id>=35*7)*(s_id<35*8)*(d_id<35*8)+' +
                                                                               '(s_id>=35*8)*(d_id>=35*8)*(s_id<35*9)*(d_id<35*9)+' +
                                                                               '(s_id>=35*9)*(d_id>=35*9)*(s_id<35*10)*(d_id<35*10)+' +
                                                                               '(s_id>=35*10)*(d_id>=35*10)*(s_id<35*11)*(d_id<35*11)+' +
                                                                               '(s_id>=35*11)*(d_id>=35*11)*(s_id<35*12)*(d_id<35*12)+' +
                                                                               '(s_id>=35*12)*(d_id>=35*12)*(s_id<35*13)*(d_id<35*13)+' +
                                                                               '(s_id>=35*13)*(d_id>=35*13)*(s_id<35*14)*(d_id<35*14)+' +
                                                                               '(s_id>=35*14)*(d_id>=35*14)*(s_id<35*15)*(d_id<35*15)+' +
                                                                               '(s_id>=35*15)*(d_id>=35*15)*(s_id<35*16)*(d_id<35*16)+' +
                                                                               '(s_id>=35*16)*(d_id>=35*16)*(s_id<35*17)*(d_id<35*17)+' +
                                                                               '(s_id>=35*17)*(d_id>=35*17)*(s_id<35*18)*(d_id<35*18)+' +
                                                                               '(s_id>=35*18)*(d_id>=35*18)*(s_id<35*19)*(d_id<35*19)+' +
                                                                               '(s_id>=35*19)*(d_id>=35*19)*(s_id<35*20)*(d_id<35*20)+' +
                                                                               '(s_id>=35*20)*(d_id>=35*20)*(s_id<35*21)*(d_id<35*21)+' +
                                                                               '(s_id>=35*21)*(d_id>=35*21)*(s_id<35*22)*(d_id<35*22)+' +
                                                                               '(s_id>=35*22)*(d_id>=35*22)*(s_id<35*23)*(d_id<35*23)+' +
                                                                               '(s_id>=35*23)*(d_id>=35*23)*(s_id<35*24)*(d_id<35*24)+' +
                                                                               '(s_id>=35*24)*(d_id>=35*24)*(s_id<35*25)*(d_id<35*25)+' +
                                                                               '(s_id>=35*25)*(d_id>=35*25)*(s_id<35*26)*(d_id<35*26)+' +
                                                                               '(s_id>=35*26)*(d_id>=35*26)*(s_id<35*27)*(d_id<35*27)+' +
                                                                               '(s_id>=35*27)*(d_id>=35*27)*(s_id<35*28)*(d_id<35*28)+' +
                                                                               '(s_id>=35*28)*(d_id>=35*28)*(s_id<35*29)*(d_id<35*29)+' +
                                                                               '(s_id>=35*29)*(d_id>=35*29)*(s_id<35*30)*(d_id<35*30)+' +
                                                                               '(s_id>=35*30)*(d_id>=35*30)*(s_id<35*31)*(d_id<35*31)+' +
                                                                               '(s_id>=35*31)*(d_id>=35*31)*(s_id<35*32)*(d_id<35*32)+' +
                                                                               '(s_id>=35*32)*(d_id>=35*32)*(s_id<35*33)*(d_id<35*33)+' +
                                                                               '(s_id>=35*33)*(d_id>=35*33)*(s_id<35*34)*(d_id<35*34)+' +
                                                                               '(s_id>=35*34)*(d_id>=35*34)*(s_id<35*35)*(d_id<35*35)+' +
                                                                               '(s_id>=35*35)*(d_id>=35*35)*(s_id<35*36)*(d_id<35*36)+' +
                                                                               '(s_id>=35*36)*(d_id>=35*36)*(s_id<35*37)*(d_id<35*37)+' +
                                                                               '(s_id>=35*37)*(d_id>=35*37)*(s_id<35*38)*(d_id<35*38)+' +
                                                                               '(s_id>=35*38)*(d_id>=35*38)*(s_id<35*39)*(d_id<35*39)+' +
                                                                               '(s_id>=35*39)*(d_id>=35*39)*(s_id<35*40)*(d_id<35*40)' +
                                                                               ')')#, partition=True)#

    
                                                                                   '(s_id>=140*0)*(d_id>=140*0)*(s_id<140*1)*(d_id<140*1)+' +
                                                                               '(s_id>=140*1)*(d_id>=140*1)*(s_id<140*2)*(d_id<140*2)+' +
                                                                               '(s_id>=140*2)*(d_id>=140*2)*(s_id<140*3)*(d_id<140*3)+' +
                                                                               '(s_id>=140*3)*(d_id>=140*3)*(s_id<140*4)*(d_id<140*4)+' +
                                                                               '(s_id>=140*4)*(d_id>=140*4)*(s_id<140*5)*(d_id<140*5)+' +
                                                                               '(s_id>=140*5)*(d_id>=140*5)*(s_id<140*6)*(d_id<140*6)+' +
                                                                               '(s_id>=140*6)*(d_id>=140*6)*(s_id<140*7)*(d_id<140*7)+' +
                                                                               '(s_id>=140*7)*(d_id>=140*7)*(s_id<140*8)*(d_id<140*8)+' +
                                                                               '(s_id>=140*8)*(d_id>=140*8)*(s_id<140*9)*(d_id<140*9)+' +
                                                                               '(s_id>=140*9)*(d_id>=140*9)*(s_id<140*10)*(d_id<140*10)' +'''

    #SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='GLU_cluster', connectivity='(s_id!=d_id)*(sy>=20)*(dy>=20)')

    e_ng.add_behaviour(9, SORN_K_random_input())

    if __name__ == '__main__' and attrs.get('UI', False):
        e_ng.color = get_color(0, 1)

    SORN.set_marked_variables(attrs['ind'], info=print_info, storage_manager=sm)
    SORN.initialize(info=False)

    #for i, syn in enumerate(SORN['syn']):
    #    syn.enabled = np.load('Data/E{}.npy'.format(i))
    #    syn.W = np.load('Data/W{}.npy'.format(i))

    ###################################################################################################################

    if __name__ == '__main__' and attrs.get('UI', False):
        Network_UI(SORN, label='SORN UI K_WTA', storage_manager=sm, group_display_count=1, reduced_layout=False).show()

    score = 0
    plastic_steps = attrs.get('plastic', 20000)

    for i in range(1):
        sm = StorageManager(attrs['name'] + '[{:03d}]'.format(i + 1), random_nr=True, print_msg=print_info)
        sm.save_param_dict(attrs)
        score += train_and_generate_text(SORN, plastic_steps, 5000, 1000, display=print_info, stdp_off=True, same_timestep_without_feedback_loop=True, steps_recovery=1000, storage_manager=sm)

    print('score=', score)

    return score


if __name__ == '__main__':
    #ind = []#[72.7255592339286, 29.458175070582683, 0.00015704485382051904, 0.006763629096129458, 0.11926664091843557, 0.5031562876644946, 0.035971677467027625, 0.00014754543834789394]#[]
    #ind = [91.28948124066251, 25.70311259727637, 0.00011958137352069863, 0.007103970516674569, 0.08764929945250621, 0.45626446218228583, 0.03506439143087593, 0.00012216591033475477]
    ind = []

    default_modules[1] = multi_group_plot_tab(['output', 'exhaustion_value', 'weight_norm_factor'])#, 'nox', 'refractory_counter'
    default_modules[18] = single_group_plot_tab({'activity': (0, 0, 0), 'excitation': (0, 0, 255), 'inhibition': (255, 0, 0), 'input_act': (255, 0, 255), 'exhaustion_value': (0, 255, 0)})

    print('score', run(attrs={'name': 'adsfdsfsdf', 'ind': ind, 'N_e': 1400, 'TS': [1], 'UI': True, 'ff': True, 'fb': False, 'plastic': 30000}))#30000 #50p log just exc 0.04