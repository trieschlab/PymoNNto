from PymoNNto.Exploration.Network_UI.TabBase import *
import random

class single_group_plot_tab(TabBase):

    def __init__(self, variables=['output', 'excitation', 'inhibition'], colors=[(0, 0, 0), (0, 0, 255), (255, 0, 0), (155, 0, 155), (0, 155, 0), (155, 155, 0), (0, 155, 155)], net_lines=[], neuron_lines=[], title='Single Group', timesteps=500):
        super().__init__(title)
        self.variables = {}
        self.colors = colors
        self.net_lines = net_lines
        self.neuron_lines = neuron_lines
        for i, v in enumerate(variables):
            self.variables[v] = self.get_color(i)
        self.timesteps=timesteps

    def get_color(self, i):
        if i < len(self.colors):
            return self.colors[i]
        else:
            return (random.randint(0,255),random.randint(0,255),random.randint(0,255))


    def add_recorder_variables(self, neuron_group, Network_UI):

        for var in self.variables:
            if hasattr(neuron_group, var):
                Network_UI.add_recording_variable(neuron_group, 'n.'+var, timesteps=self.timesteps)
                Network_UI.add_recording_variable(neuron_group, 'np.mean(n.'+var+')', timesteps=self.timesteps)

    def initialize(self, Network_UI):
        self.inh_exc_tab = Network_UI.Next_Tab(self.title, stretch=0)

        self.group_title_label = Network_UI.Add_element(QLabel('NeuronGroup'))

        Network_UI.Next_H_Block()

        tooltip_message = ''#str(self.variables).replace(',', '\r\n')
        for key in self.variables:
            tooltip_message+=str(self.variables[key])+' : '+str(key)+'\r\n'

        single_vars = list(self.variables.keys())
        mean_vars = ['np.mean(n.'+var+')' for var in self.variables]
        colors = list(self.variables.values())

        mean_curves = Network_UI.Add_plot_curve(y_label='NeuronGroup ' + str(single_vars), number_of_curves=len(mean_vars), names=mean_vars, colors=colors, lines=self.net_lines, tooltip_message=tooltip_message, return_list=True)
        self.net_curves=dict(zip(self.variables, mean_curves))

        Network_UI.Next_H_Block(stretch=0)

        self.neuron_title_label = Network_UI.Add_element(QLabel('Selected Neuron'))

        Network_UI.Next_H_Block()

        single_curves = Network_UI.Add_plot_curve(y_label='Neuron ' + str(single_vars), number_of_curves=len(single_vars), names=single_vars, colors=colors, lines=self.neuron_lines, tooltip_message=tooltip_message, return_list=True)
        self.neuron_curves = dict(zip(self.variables, single_curves))

        Network_UI.Next_H_Block(stretch=0)

        self.line_checkboxes = {}
        for var in self.variables:
            c=self.variables[var]
            txt='<font color='+('#%02x%02x%02x'%c).upper()+'>'+var+'</font>'
            Network_UI.Add_element(QLabel(txt))

        Network_UI.Next_H_Block(stretch=0)

        for var in self.variables:
            self.line_checkboxes[var] = Network_UI.Add_element(QCheckBox(''))
            self.line_checkboxes[var].setChecked(True)

    def update(self, Network_UI):
        if self.inh_exc_tab.isVisible():
            group = Network_UI.network[Network_UI.neuron_select_group, 0]

            self.group_title_label.setText('NeuronGroup ('+Network_UI.neuron_select_group+')')

            for var in self.variables:
                iterations = group['n.iteration', 0, 'np'][-self.timesteps:]

                try:
                    if self.line_checkboxes[var].isChecked():
                        mean_var = 'np.mean(n.'+var+')'
                        data_mean = group[mean_var, 0, 'np'][-self.timesteps:]
                        self.net_curves[var].setData(iterations, data_mean)
                    else:
                        self.net_curves[var].clear()
                except:
                    self.net_curves[var].clear()
                    #print(var, "cannot be evaluated")

                try:
                    if self.line_checkboxes[var].isChecked():
                        single_var = 'n.' + var
                        data_neuron = group[single_var, 0, 'np'][-self.timesteps:, Network_UI.neuron_select_id].astype(def_dtype)
                        self.neuron_curves[var].setData(iterations, data_neuron)
                    else:
                        self.neuron_curves[var].clear()
                except:
                    self.neuron_curves[var].clear()
                    #print(var, "cannot be evaluated")

