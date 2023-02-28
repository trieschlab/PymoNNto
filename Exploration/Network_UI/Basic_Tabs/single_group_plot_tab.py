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
                Network_UI.add_recording_variable(neuron_group, var, timesteps=self.timesteps)
                Network_UI.add_recording_variable(neuron_group, 'np.mean('+var+')', timesteps=self.timesteps)

    def initialize(self, Network_UI):
        self.inh_exc_tab = Network_UI.add_tab(title=self.title, stretch=0) #Network_UI.Next_Tab(self.title, stretch=0)

        self.group_title_label = Network_UI.tab.add_widget(QLabel('NeuronGroup'))

        Network_UI.tab.add_row()

        tooltip_message = ''
        for key in self.variables:
            tooltip_message+=str(self.variables[key])+' : '+str(key)+'\r\n'

        single_vars = list(self.variables.keys())
        mean_vars = ['np.mean('+var+')' for var in self.variables]
        colors = list(self.variables.values())

        mean_curves = Network_UI.tab.add_plot(y_label='NeuronGroup ' + str(single_vars), tooltip_message=tooltip_message).add_curves(number_of_curves=len(mean_vars), names=mean_vars, colors=colors, lines=self.net_lines)
        self.net_curves=dict(zip(self.variables, mean_curves))

        Network_UI.tab.add_row(stretch=0)

        self.neuron_title_label = Network_UI.tab.add_widget(QLabel('Selected Neuron'))

        Network_UI.tab.add_row()

        single_curves = Network_UI.tab.add_plot(y_label='Neuron ' + str(single_vars), tooltip_message=tooltip_message).add_curves(number_of_curves=len(single_vars), names=single_vars, colors=colors, lines=self.neuron_lines)
        self.neuron_curves = dict(zip(self.variables, single_curves))

        Network_UI.tab.add_row(stretch=0)

        self.line_checkboxes = {}
        for var in self.variables:
            c=self.variables[var]
            txt='<font color='+('#%02x%02x%02x'%c).upper()+'>'+var+'</font>'
            Network_UI.tab.add_widget(QLabel(txt))

        Network_UI.tab.add_row(stretch=0)

        for var in self.variables:
            self.line_checkboxes[var] = Network_UI.tab.add_widget(QCheckBox(''))
            self.line_checkboxes[var].setChecked(True)

    def update(self, Network_UI):
        if self.inh_exc_tab.isVisible():
            group = Network_UI.selected_neuron_group()

            self.group_title_label.setText('NeuronGroup ('+Network_UI.selected_neuron_group().tags[0]+')')

            for var in self.variables:
                if hasattr(group, var):
                    iterations = group['iteration', 0, 'np'][-self.timesteps:]

                    try:
                        if self.line_checkboxes[var].isChecked():
                            mean_var = 'np.mean('+var+')'
                            data_mean = group[mean_var, 0, 'np'][-self.timesteps:]
                            self.net_curves[var].setData(iterations, data_mean)
                        else:
                            self.net_curves[var].setData([],[])#clear()
                    except:
                        self.net_curves[var].setData([],[])

                    try:
                        if self.line_checkboxes[var].isChecked():
                            single_var = var
                            data_neuron = group[single_var, 0, 'np'][-self.timesteps:, Network_UI.selected_neuron_id()].astype(Network_UI.network.def_dtype)
                            self.neuron_curves[var].setData(iterations, data_neuron)
                        else:
                            self.neuron_curves[var].setData([],[])
                    except:
                        self.neuron_curves[var].setData([],[])

