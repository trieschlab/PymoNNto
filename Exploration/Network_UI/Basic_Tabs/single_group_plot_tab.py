from SORNSim.Exploration.Network_UI.TabBase import *

class single_group_plot_tab(TabBase):

    def __init__(self, variables, title='single group', timesteps=500):
        super().__init__(title)
        self.variables = variables
        self.timesteps=timesteps

    def add_recorder_variables(self, neuron_group, Network_UI):

        for var in self.variables:
            if hasattr(neuron_group, var):
                Network_UI.add_recording_variable(neuron_group, 'n.'+var, timesteps=self.timesteps)
                Network_UI.add_recording_variable(neuron_group, 'np.mean(n.'+var+')', timesteps=self.timesteps)



    def initialize(self, Network_UI):
        self.inh_exc_tab = Network_UI.Next_Tab(self.title)


        tooltip_message = ''#str(self.variables).replace(',', '\r\n')
        for key in self.variables:
            tooltip_message+=str(self.variables[key])+' : '+str(key)+'\r\n'

        single_vars = list(self.variables.keys())
        mean_vars = ['np.mean(n.'+var+')' for var in self.variables]
        colors = list(self.variables.values())

        mean_curves = Network_UI.Add_plot_curve('NeuronGroup' + str(single_vars), number_of_curves=len(mean_vars), names=mean_vars, colors=colors, lines=[0], tooltip_message=tooltip_message)
        self.net_curves=dict(zip(self.variables, mean_curves))

        Network_UI.Next_H_Block()

        single_curves = Network_UI.Add_plot_curve('Neuron' + str(single_vars), number_of_curves=len(single_vars), names=single_vars, colors=colors, lines=[0], tooltip_message=tooltip_message)
        self.neuron_curves = dict(zip(self.variables, single_curves))

        #Network_UI.Next_H_Block()


    def update(self, Network_UI):
        if self.inh_exc_tab.isVisible():
            group = Network_UI.network[Network_UI.neuron_select_group, 0]

            #rec = Network_UI.rec(group, self.timesteps)

            for var in self.variables:
                if hasattr(group, var):
                    iterations = group['n.iteration', 0, 'np'][-self.timesteps:]

                    mean_var = 'np.mean(n.'+var+')'
                    single_var = 'n.'+var

                    data_mean = group[mean_var, 0, 'np'][-self.timesteps:]
                    self.net_curves[var].setData(iterations, data_mean)

                    data_neuron = group[single_var, 0, 'np'][-self.timesteps:, Network_UI.neuron_select_id]
                    self.neuron_curves[var].setData(iterations, data_neuron)
