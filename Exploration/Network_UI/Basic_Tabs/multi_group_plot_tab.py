from PymoNNto.Exploration.Network_UI.TabBase import *

class multi_group_plot_tab(TabBase):

    def __init__(self, variables, title='Multi Group', timesteps=500):
        super().__init__(title)
        self.timesteps = timesteps

        self.original_variables=variables
        self.variables = []
        self.curve_numbers = []
        self.plot_variables = []
        self.ptv = {}
        for i, var in enumerate(self.original_variables):#grouped togerther with var1|var2
            splitted=var.split('|')

            for i in range(len(splitted)):
                if is_number(splitted[i]):
                    new_var_name = '_plot_tab_var_' + str(i)
                    self.ptv[new_var_name] = float(splitted[i])
                    splitted[i] = new_var_name

            for v in splitted:
                self.variables.append(v)

            self.curve_numbers.append(len(splitted))
            self.plot_variables.append(splitted)





    def add_recorder_variables(self, neuron_group, Network_UI):
        for var in self.variables:
            if '_plot_tab_var_' in var:
                setattr(neuron_group, var, self.ptv[var])

            Network_UI.add_recording_variable(neuron_group, 'np.mean(' + var + ')', timesteps=self.timesteps)
            Network_UI.add_recording_variable(neuron_group, var, timesteps=self.timesteps)



    def initialize(self, Network_UI):
        self.main_tab = Network_UI.add_tab(title=self.title)

        group_count = len(Network_UI.get_visible_neuron_groups())

        self.net_plot_dicts = []

        for plot_id, plot_variable_list in enumerate(self.plot_variables):

            curves_per_plot = len(plot_variable_list)

            stretch = 1
            if plot_id == 0:
                stretch = 2

            labels = []
            for var in plot_variable_list:
                if '_plot_tab_var_' in var:
                    labels.append(str(self.ptv[var]))
                else:
                    labels.append(var)


            curves = Network_UI.tab.add_plot(stretch=stretch, x_label='t (iterations)', y_label='Network average ' + str(labels)).add_curves(number_of_curves=group_count*curves_per_plot) #, lines=lines #plot_variable_list

            ci=0
            plot_curve_dict = {}
            for var in plot_variable_list:
                variable_curves = []
                for group_index in range(group_count):
                    variable_curves.append(curves[ci])
                    ci += 1
                plot_curve_dict[var] = variable_curves
            self.net_plot_dicts.append(plot_curve_dict)

        Network_UI.tab.add_row()

        self.neuron_plot_dicts = []

        for plot_id, plot_variable_list in enumerate(self.plot_variables):

            curves_per_plot = len(plot_variable_list)

            stretch = 1
            if plot_id == 0:
                stretch = 2

            curves = Network_UI.tab.add_plot(stretch=stretch, x_label='t (iterations)', y_label='Neuron ' + str(plot_variable_list)).add_curves(number_of_curves=1 + curves_per_plot, colors=[Network_UI.neuron_select_color], legend=False)

            ci=0
            plot_curve_dict = {}
            for var in plot_variable_list:
                plot_curve_dict[var] = curves[ci]
                ci += 1
            self.neuron_plot_dicts.append(plot_curve_dict)



        #if Network_UI.group_display_count > 1:
        #    Network_UI.tab.add_row()

        #    self.group_sliders = []
        #    for group_index in range(Network_UI.group_display_count):
        #        self.group_sliders.append(QSlider(1))  # QtCore.Horizontal
        #        self.group_sliders[-1].setMinimum(0)
        #        self.group_sliders[-1].setMaximum(100)
        #        self.group_sliders[-1].setSliderPosition(100)
        #        self.group_sliders[-1].mouseReleaseEvent = Network_UI.static_update_func
        #        self.group_sliders[-1].setToolTip('scale neuron-group plots up and down (only visualization)')

        #        Network_UI.tab.add_widget(self.group_sliders[-1])


    def update(self, Network_UI):
        if self.main_tab.isVisible():

            for curve_dict in self.net_plot_dicts:
                for variable in curve_dict:
                    for group_id, curve in enumerate(curve_dict[variable]):
                        group = Network_UI.network.NeuronGroups[group_id]#get_visible_neuron_groups()[group_id]
                        if group.is_visible:
                            #group = Network_UI.network[group_tag, 0]

                            squeeze = group.slider.sliderPosition() / 100

                            try:
                                net_data = group['np.mean(' + variable + ')', 0, 'np'][-self.timesteps:]
                                iterations = group['iteration', 0, 'np'][-self.timesteps:]
                                curve.setData(iterations, net_data * squeeze, pen=group.color)
                            except:  # else:
                                curve.clear()
                        else:
                            curve.clear()

            group = Network_UI.selected_neuron_group()

            for curve_dict in self.neuron_plot_dicts:
                for variable in curve_dict:
                    curve = curve_dict[variable]

                    try:
                        neuron_data = group[variable, 0, 'np'][-self.timesteps:].astype(Network_UI.network.def_dtype)#for bool
                        iterations = group['iteration', 0, 'np'][-self.timesteps:]
                        if len(neuron_data.shape) > 1:
                            neuron_data = np.mean(neuron_data[:, Network_UI.selected_neuron_mask()], axis=1)
                        curve.setData(iterations, neuron_data)
                    except:
                        curve.setData([], [])
