from SORNSim.NetworkBehaviour.Logic.Basics.BasicHomeostasis import *
import scipy.sparse as sp

class SORN_Input_collect(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('collect')
        neurons.iteration_lag = self.get_init_attr('iteration_lag', 1, neurons)

        neurons.require_synapses('GLU')
        neurons.require_synapses('GABA')

        neurons.inh_strength = self.get_init_attr('inh_strength', 1.0, neurons)

        neurons.x = (np.random.random(neurons.size) < 0.5) + 0
        neurons.T_min = self.get_init_attr('T_min', 0.0, neurons)
        neurons.T_max = self.get_init_attr('T_max', 0.5, neurons)
        neurons.T = neurons.T_min + np.random.random(neurons.size) * (neurons.T_max - neurons.T_min)
        neurons.input_gain = self.get_init_attr('input_gain', 1.0, neurons)
        neurons.sigma = self.get_init_attr('sigma', None, neurons)
        neurons.R_x = np.zeros(neurons.size)
        neurons.lamb = self.get_init_attr('lamb', -1, neurons)#10 -1=full
        neurons.x_new = np.zeros(neurons.size)
        neurons.input = np.zeros(neurons.size)

        neurons.FSC = self.get_init_attr('fixed_synapse_count', False, neurons)

        #todo: calculate distributed lamb for every synapse group

        for s in neurons.afferent_synapses['GLU']:
            syn_lamb = neurons.lamb#*s.get_synapse_group_size_factor(neurons, 'GLU')
            if neurons.lamb == -1:
                syn_lamb = neurons.size

            if neurons.FSC:
                s.W = s.get_random_synapse_mat_fixed(syn_lamb)*s.enabled
            else:
                s.W = s.get_random_synapse_mat(density=syn_lamb / float(neurons.size))*s.enabled
            s.enabled *= (s.W > 0)


        for s in neurons.afferent_synapses['GLU']:
            if 'sparse' in s.tags:
                s.W = sp.csc_matrix(s.W)
                #s.W.eliminate_zeros()

        for s in neurons.afferent_synapses['GABA']:
            s.W = s.get_random_synapse_mat()

        self.normalize_synapse_attr('W', 'W', 1.0, neurons, 'GLU')
        self.normalize_synapse_attr('W', 'W', 1.0, neurons, 'GABA')


    def new_iteration(self, neurons):

        #if neurons.size == 600:
        #    print(neurons.iteration % neurons.iteration_lag)

        for s in neurons.afferent_synapses['GLU']:
            neurons.R_x += s.W.dot(s.src.x) /neurons.iteration_lag

        #neurons.x_without_input = neurons.R_x.copy()

        for s in neurons.afferent_synapses['GABA']:
            neurons.R_x -= (s.W.dot(s.src.x)*neurons.inh_strength) /neurons.iteration_lag

        neurons.R_x += neurons.input_gain * neurons.input /neurons.iteration_lag

        #if neurons.iteration % neurons.iteration_lag == 0:#Delayed
        if neurons.iteration % neurons.iteration_lag == neurons.iteration_lag - 1:
            neurons.R_x -= neurons.T

            if neurons.sigma!=None:
                neurons.R_x += neurons.sigma * np.random.rand(neurons.size)

            neurons.x_new = (neurons.R_x >= 0.0) + 0.0
            neurons.R_x *= 0





class SORN_STDP(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('STDP')
        neurons.eta_stdp = self.get_init_attr('eta_stdp', 0.005, neurons)
        neurons.prune_stdp = self.get_init_attr('prune_stdp', False, neurons)

        for s in neurons.afferent_synapses['GLU']:
            s.STDP_src_lag_buffer_old = np.zeros(neurons.size)
            s.STDP_src_lag_buffer_new = np.zeros(neurons.size)

    def new_iteration(self, neurons):
        if neurons.learning:

            for s in neurons.afferent_synapses['GLU']:

                s.STDP_src_lag_buffer_new += s.src.x_new/neurons.iteration_lag

                #buffer previous states

                if neurons.iteration % neurons.iteration_lag == neurons.iteration_lag - 1:

                    from_old = s.STDP_src_lag_buffer_old#
                    from_new = s.STDP_src_lag_buffer_new#s.src.x_new#

                    to_old = s.dst.x
                    to_new = s.dst.x_new

                    if 'sparse' in s.tags:

                        col = np.repeat(np.arange(s.W.shape[1]), np.diff(s.W.indptr))  # s.W.indptr
                        row = s.W.indices
                        data = s.W.data
                        data += neurons.eta_stdp * (
                        to_new[row] * from_old[col] - to_old[row] * from_new[col])  # ????????????????
                        s.W[s.W < 0] = 0

                        if neurons.prune_stdp:
                            s.W.data[s.W.data < 1e-10] = 0.  # eliminate small weights
                            s.W.eliminate_zeros()

                    else:

                        dw = neurons.eta_stdp * (
                        to_new[:, None] * from_old[None, :] - to_old[:, None] * from_new[None, :])

                        s.W += dw * s.enabled
                        s.W[s.W < 0.0] = 0.0

                        if neurons.prune_stdp:
                            s.W[s.W < 1e-10] = 0

                        s.enabled *= (s.W > 0)

                        # print('STDP',s.W.sum())

                    #clear buffer
                    s.STDP_src_lag_buffer_old = s.STDP_src_lag_buffer_new.copy()
                    s.STDP_src_lag_buffer_new = np.zeros(neurons.size)



class SORN_SN(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('SN')
        self.syn_type = self.get_init_attr('syn_type', 'GLU', neurons)


    def new_iteration(self, neurons):
        if neurons.iteration % neurons.iteration_lag == neurons.iteration_lag-1:
            self.normalize_synapse_attr('W', 'W', 1.0, neurons, self.syn_type)


class SORN_iSTDP(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('iSTDP')
        neurons.eta_istdp = self.get_init_attr('eta_istdp', 0.001, neurons)
        neurons.h_ip = self.get_init_attr('h_ip', 0.1, neurons)

    def new_iteration(self, neurons):
        if neurons.learning:
            if neurons.iteration % neurons.iteration_lag == neurons.iteration_lag - 1:
                for s in neurons.afferent_synapses['GABA']:
                    s.W += -neurons.eta_istdp*((1-(s.dst.x[:, None]*(1+1.0/neurons.h_ip))) * s.src.x[None, :])
                    s.W[s.W <= 0] = 0.001
                    s.W[s.W > 1.0] = 1.0


class SORN_diffuse_IP(Time_Integration_Homeostasis):

    def set_variables(self, neurons):
        self.add_tag('diff_IP')
        super().set_variables(neurons)
        self.measurement_param = 'x_new'
        self.adjustment_param = 'T'
        self.measure_group_sum = True

        self.set_threshold(self.get_init_attr('h_dh', 0.1, neurons))
        self.adj_strength = -self.get_init_attr('eta_dh', 0.001, neurons)


    def new_iteration(self, neurons):
        if True:#neurons.learning:
            if neurons.iteration % neurons.iteration_lag == neurons.iteration_lag-1:
                super().new_iteration(neurons)


class SORN_IP_New(Instant_Homeostasis):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.add_tag('IP')
        self.measurement_param = 'x_new'
        self.adjustment_param = 'T'

        self.set_threshold(self.get_init_attr('h_ip', 0.1, neurons), self.get_init_attr('gap_percent', None, neurons))
        self.adj_strength = -self.get_init_attr('eta_ip', 0.001, neurons)

        #target_clip_min
        #target_clip_max

    def new_iteration(self, neurons):
        if True:#neurons.learning:
            if neurons.iteration % neurons.iteration_lag == neurons.iteration_lag-1:
                super().new_iteration(neurons)


class SORN_IP_TI(Time_Integration_Homeostasis):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.add_tag('IPTI')
        self.measurement_param = 'x_new'
        self.adjustment_param = 'T'

        self.set_threshold(self.get_init_attr('h_ip', 0.1, neurons))
        self.adj_strength = -self.get_init_attr('eta_ip', 0.001, neurons)

        #target_clip_min
        #target_clip_max

    def new_iteration(self, neurons):
        if True:#neurons.learning:
            if neurons.iteration % neurons.iteration_lag == neurons.iteration_lag-1:
                super().new_iteration(neurons)


#class SORN_IP(TRENNeuronBehaviour):

#    def set_variables(self, neurons):
#        neurons.h_ip = self.get_init_attr('h_ip', 0.1, neurons)
#        neurons.eta_ip = self.get_init_attr('eta_ip', 0.001, neurons)


#    def new_iteration(self, neurons):
#        if neurons.iteration % neurons.iteration_lag == 0:
#            neurons.T += neurons.eta_ip*(neurons.x_new - neurons.h_ip)
#            #neurons.T = np.clip(neurons.T, neurons.T_min, neurons.T_max) todo:???


class SORN_SP(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('SP')
        neurons.sp_prob = self.get_init_attr('sp_prob', 0.1, neurons)#???default
        neurons.sp_init = self.get_init_attr('sp_init', 0.001, neurons)#???default
        self.syn_type = self.get_init_attr('syn_type', 'GLU', neurons)

    def new_iteration(self, neurons):
        if neurons.iteration % neurons.iteration_lag == neurons.iteration_lag-1:
            for s in neurons.afferent_synapses[self.syn_type]:
                if np.random.rand() < neurons.sp_prob:
                    counter = 0
                    while True:
                        i = np.random.randint(s.dst.size)
                        j = np.random.randint(s.src.size)
                        connected = s.W[i, j] > 0
                        valid = (i != j)
                        if (valid and not connected) or counter == 1000:
                            break
                        if valid and connected:
                            counter += 1

                    if counter < 1000:
                        if 'sparse' in s.tags:
                            # include new connection
                            # temporaly convert to dok for easier update
                            W_dok = s.W.todok()
                            W_dok[i, j] = neurons.sp_init
                            s.W = W_dok.tocsc()
                        else:
                            s.W[i, j] = neurons.sp_init
                            s.enabled[i, j] = True
                    else:
                        print('\nCould not find a new connection\n')




class SORN_finish(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('finish')

    def new_iteration(self, neurons):
        if neurons.iteration % neurons.iteration_lag == neurons.iteration_lag-1:#last step not first!!!!!!!!
            neurons.x = neurons.x_new




#class SORN_diffuse_homeostasis(TRENNeuronBehaviour):
#
#    def set_variables(self, neurons):
#        neurons.h_dh = self.get_init_attr('h_dh', 0.1, neurons)
#        neurons.eta_dh = self.get_init_attr('eta_dh', 0.001, neurons)
#
#    def new_iteration(self, neurons):
#        if neurons.iteration % neurons.iteration_lag == 0:
#            group_avg_act = np.sum(neurons.x_new)/neurons.size
#            neurons.h_ip += neurons.eta_dh * (group_avg_act - neurons.h_dh)



