from PymoNNto.NetworkCore.Behavior import *
import numpy as np


class neuron_event(Behavior):

    def initialize(self, neurons):
        self.condition = self.parameter('condition', 'False', None)#'s.src.spike==1'
        self.compiled_condition = compile(self.condition, '<string>', 'eval')

        self.formula = self.parameter('eq', None)

        for neuron_var in sorted(neurons.__dict__, key=len, reverse=True):
            self.formula = self.formula.replace('n.' + neuron_var, 'neurons.' + neuron_var + '[indx]')

        self.compiled_formula = compile(self.formula, '<string>', 'exec')

    def event(self, neurons, condition_mask=True):
        n = neurons
        for indx in np.where(condition_mask):
            exec(self.compiled_formula)

    def iteration(self, neurons):
        n=neurons
        self.event(neurons, condition_mask=eval(self.compiled_condition))

class syn_event(Behavior):

    def initialize(self, synapse):
        s=synapse
        self.src_condition = self.parameter('src_condition', 'True', None)#'s.src.spike==1'
        self.compiled_src_condition = compile(self.src_condition, '<string>', 'eval')

        self.dst_condition = self.parameter('dst_condition', 'True', None)#'s.dst.spike==1'
        self.compiled_dst_condition = compile(self.dst_condition, '<string>', 'eval')

        self.formula = self.parameter('eq', None)#eq_split()

        for syn_var in sorted(synapse.__dict__, key=len, reverse=True):
            self.formula = self.formula.replace('s.'+syn_var, 'synapse.'+syn_var+'[src_indx,dst_indx]')

        for src_var in sorted(synapse.src.__dict__, key=len, reverse=True):
            self.formula = self.formula.replace('src.'+src_var, 'source.'+src_var+'[src_indx]')

        for dst_var in sorted(synapse.dst.__dict__, key=len, reverse=True):
            self.formula = self.formula.replace('dst.' + dst_var, 'destination.' + dst_var + '[dst_indx]')

        self.compiled_formula = compile(self.formula, '<string>', 'exec')

    def event(self, synapse, src_mask=True, dst_mask=True):
        destination = synapse.dst
        source = synapse.src

        if type(src_mask) is bool and src_mask:
            src_indxes = range(synapse.src.size)
        else:
            src_indxes = np.where(src_mask)[0]

        if type(dst_mask) is bool:
            dst_indxes = range(synapse.dst.size)
        else:
            dst_indxes = np.where(dst_mask)[0]

        for src_indx in src_indxes:
            for dst_indx in dst_indxes:
                #print(self.formula, src_indx, dst_indx)
                exec(self.compiled_formula)
                #print(synapse.w)

        #print(s.src.v)

class on_pre(syn_event):
    def iteration(self, synapse):
        destiantion = synapse.dst
        source = synapse.src
        dst = synapse.dst
        src = synapse.src
        self.event(synapse, src_mask=eval(self.compiled_src_condition))

class on_post(syn_event):
    def iteration(self, synapse):
        destiantion = synapse.dst
        source = synapse.src
        dst = synapse.dst
        src = synapse.src
        self.event(synapse, dst_mask=eval(self.compiled_dst_condition))

class on_simu(syn_event):
    def iteration(self, synapse):
        destiantion = synapse.dst
        source = synapse.src
        dst = synapse.dst
        src = synapse.src
        self.event(synapse, src_mask=eval(self.compiled_src_condition), dst_mask=eval(self.compiled_dst_condition))


#class on_pre(EquationModule):

#    def initialize(self, synapse):
#        formula = eq_split(self.parameter('eq', None))

#    def iteration(self, synapse):
#        pre_mask = synapse.src.spike



