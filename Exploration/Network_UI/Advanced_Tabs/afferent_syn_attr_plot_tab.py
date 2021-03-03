from PymoNNto.Exploration.Network_UI.TabBase import *


class afferent_syn_attr_plot_tab(TabBase):

    def __init__(self, syn_vars, title='Aff Syn',timesteps=500):
        super().__init__(title)
        self.syn_vars=syn_vars
        self.timesteps=timesteps

    def add_recorder_variables(self, neuron_group, Network_UI):
        self.check={}
        for syn_var in self.syn_vars:
            self.check[syn_var] = True
            for syn in neuron_group.afferent_synapses["All"]:
                if not hasattr(syn, syn_var):
                    self.check[syn_var] = False
            if self.check[syn_var]:
                Network_UI.add_recording_variable(neuron_group, '[np.sum(s.'+syn_var+') for s in n.afferent_synapses["All"]]', timesteps=self.timesteps)

    def initialize(self, Network_UI):
        self.weight_tab = Network_UI.Next_Tab(self.title)

        self.plots = {}
        for syn_var in self.syn_vars:
            _, syn_plt = Network_UI.Add_plot_curve('Neuron Group average ' + syn_var, return_plot=True, x_label='t (iterations)', y_label='Input')
            self.plots[syn_var] = syn_plt



    def update(self, Network_UI):
        if self.weight_tab.isVisible() and len(Network_UI.network[Network_UI.neuron_select_group]) > 0:

            group = Network_UI.network[Network_UI.neuron_select_group, 0]

            for syn_var in self.syn_vars:

                if self.check[syn_var]:

                    self.plots[syn_var].clear()

                    recorded = group['[np.sum(s.'+syn_var+') for s in n.afferent_synapses["All"]]'][-self.timesteps:]
                    iterations = group['n.iteration', 0, 'np'][-self.timesteps:]
                    if len(recorded) > 0:
                        inputs = np.array(recorded[0])
                        ident=[s.src.group_without_subGroup() for s in group.afferent_synapses["All"]]
                        single_ident = list(set(ident))

                        for i, si in enumerate(single_ident):
                            mask = [id == si for id in ident]

                            data = np.sum(inputs[:, mask], axis=1)
                            curve = pg.PlotCurveItem(iterations, data, name='', pen=si.color)#self.slow_input_colors[i]
                            self.plots[syn_var].addItem(curve)
