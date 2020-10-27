from SORNSim.Exploration.Network_UI.TabBase import *

class multi_group_plot_tab(TabBase):

    def __init__(self, variables, line_dict={}, title='Multi Group', timesteps=500, tensorflow=False):
        super().__init__(title)
        self.variables = variables
        self.line_dict = line_dict
        self.timesteps = timesteps

        if tensorflow:
            self.add_str='.numpy()'
        else:
            self.add_str=''

    def add_recorder_variables(self, neuron_group, Network_UI):
        for var in self.variables:
            if hasattr(neuron_group, var):
                Network_UI.add_recording_variable(neuron_group, 'n.'+var+self.add_str, timesteps=self.timesteps)
                Network_UI.add_recording_variable(neuron_group, 'np.mean(n.'+var+self.add_str+')', timesteps=self.timesteps)

        '''
        if hasattr(neuron_group, 'output'):
            recorder.add_varable('n.output')#???
            recorder.add_varable('np.mean(n.output)')
        if hasattr(neuron_group, 'TH'):
            recorder.add_varable('n.TH')
            recorder.add_varable('np.mean(n.TH)')
        if hasattr(neuron_group, 'weight_norm_factor'):
            recorder.add_varable('n.weight_norm_factor')
            recorder.add_varable('np.mean(n.weight_norm_factor)')
        if hasattr(neuron_group, 'nox'):
            recorder.add_varable('n.nox')
            recorder.add_varable('np.average(n.nox)')
        if hasattr(neuron_group, 'refractory_counter'):
            recorder.add_varable('n.refractory_counter')
        '''



    def initialize(self, Network_UI):
        self.main_tab = Network_UI.Next_Tab(self.title)

        #self.sliders = []
        #lines = []



        #if len(Network_UI.network['IPTI'])>0:

        self.net_var_curves={}
        for i, var in enumerate(self.variables):
            stretch=1
            if i==0:
                stretch=2

            if var in self.line_dict:
                ld_val=self.line_dict[var]
                if type(ld_val) is list:
                    lines=ld_val
                else:
                    lines=[ld_val]
            else:
                lines=[]

            self.net_var_curves[var] = Network_UI.Add_plot_curve(stretch=stretch, number_of_curves=len(Network_UI.neuron_visible_groups), return_list=True, x_label='t (iterations)', y_label='Network average ' + var, lines=lines)


        Network_UI.Next_H_Block()

        self.neuron_var_curves = {}
        for i, var in enumerate(self.variables):
            stretch = 1
            if i == 0:
                stretch = 2

            if var in self.line_dict:
                ld_val = self.line_dict[var]
                if type(ld_val) is list:
                    lines = ld_val
                else:
                    lines = [ld_val]
            else:
                lines = []

            self.neuron_var_curves[var] = Network_UI.Add_plot_curve(stretch=stretch, colors=[Network_UI.neuron_select_color], legend=False, x_label='t (iterations)', y_label='Neuron ' + var, lines=lines)



    def update(self, Network_UI):
        if self.main_tab.isVisible():


            for i, group_tag in enumerate(Network_UI.neuron_visible_groups):
                if len(Network_UI.network[group_tag]) > 0:
                    group=Network_UI.network[group_tag, 0]
                    squeeze= Network_UI.group_sliders[i].sliderPosition() / 100
                    #squeeze = self.sliders[i].sliderPosition() / 100

                    for var in self.variables:
                        if hasattr(group, var):
                            net_data = group['np.mean(n.'+var+self.add_str+')', 0, 'np'][-self.timesteps:]
                            iterations = group['n.iteration', 0, 'np'][-self.timesteps:]
                            self.net_var_curves[var][i].setData(iterations, net_data * squeeze, pen=group.color)
                        else:
                            self.net_var_curves[var][i].clear()


            group = Network_UI.network[Network_UI.neuron_select_group, 0]

            for var in self.variables:
                if hasattr(group, var):
                    neuron_data = group['n.' + var+self.add_str, 0, 'np'][-self.timesteps:]
                    iterations = group['n.iteration', 0, 'np'][-self.timesteps:]
                    if len(neuron_data.shape) > 1:
                        neuron_data = neuron_data[:, Network_UI.neuron_select_id]
                    self.neuron_var_curves[var].setData(iterations, neuron_data)
                else:
                    self.neuron_var_curves[var].clear()

