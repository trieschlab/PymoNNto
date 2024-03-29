from PymoNNto.Exploration.Network_UI.TabBase import *
from PymoNNto.Exploration.Visualization.Visualization_Helper import *

class criticality_tab(TabBase):

    def __init__(self, title='Criticality', param='output', mask_param='Input_Mask', timesteps=500, mask_color_add=(-100, -100, -100)):
        super().__init__(title)
        self.param = param
        self.timesteps=timesteps
        self.mask_param = mask_param
        if self.mask_param is not None:
            self.compiled_param = compile('n.'+self.mask_param, '<string>', 'eval')
            self.inverted_compiled_param = compile('np.invert(n.' + self.mask_param+')', '<string>', 'eval')
            self.mask_color_add = mask_color_add

    def add_recorder_variables(self, neuron_group, Network_UI):
        if hasattr(neuron_group, self.param):
            Network_UI.add_recording_variable(neuron_group, self.param, timesteps=self.timesteps)
        if hasattr(neuron_group, self.param):
            self.sum_tag='np.sum('+self.param+')'
            Network_UI.add_recording_variable(neuron_group, self.sum_tag, timesteps=1000)

    def initialize(self, Network_UI):
        self.criticality_tab = Network_UI.Next_Tab(self.title)

        self.avalance_size_curve, self.avalance_size_plot = Network_UI.Add_plot_curve('net avalance size plot', True, False, legend=False, x_label='Size', y_label='Probability')
        self.avalance_duration_curve, self.avalance_duration_plot = Network_UI.Add_plot_curve('net avalance duration plot', True, False, legend=False, x_label='Duration', y_label='Probability')


        #move to update...
        self.avalance_size_plot.setXRange(min=0, max=100, padding=0)
        self.avalance_size_plot.setXRange(min=0, max=100, padding=0)

        self.log = True
        self.avalance_size_plot.setLogMode(self.log, self.log)
        self.avalance_duration_plot.setLogMode(self.log, self.log)


        _, self.group_branche_estimate_plt = Network_UI.Add_plot_curve('Group Wilting Branching Estimate', True, False, number_of_curves=2, legend=False, x_label='delta t', y_label='Autocorrelation r delta t')

        self.group_scatter=pg.ScatterPlotItem()
        self.group_estimate=pg.PlotCurveItem(pen=(255,0,0))
        self.group_m_text = pg.TextItem(text='...', anchor=(0, 0))
        self.group_m_text.setPos(75, 0.5)
        self.group_test_text = pg.TextItem(text='...', anchor=(0, 0))
        self.group_test_text.setPos(75, 0.4)

        self.group_branche_estimate_plt.addItem(self.group_scatter)
        self.group_branche_estimate_plt.addItem(self.group_estimate)
        self.group_branche_estimate_plt.addItem(self.group_m_text)
        self.group_branche_estimate_plt.addItem(self.group_test_text)

        _, self.net_branche_estimate_plt = Network_UI.Add_plot_curve('Network Wilting Branching Estimate', True, False, number_of_curves=2, legend=False, x_label='delta t', y_label='Autocorrelation r delta t')

        self.net_scatter=pg.ScatterPlotItem()
        self.net_estimate=pg.PlotCurveItem(pen=(255,0,0))
        self.net_m_text = pg.TextItem(text='...', anchor=(0, 0))
        self.net_m_text.setPos(75, 0.5)
        self.net_test_text = pg.TextItem(text='...', anchor=(0, 0))
        self.net_test_text.setPos(75, 0.4)

        self.net_branche_estimate_plt.addItem(self.net_scatter)
        self.net_branche_estimate_plt.addItem(self.net_estimate)
        self.net_branche_estimate_plt.addItem(self.net_m_text)
        self.net_branche_estimate_plt.addItem(self.net_test_text)

        self.WP_test_execute = False
        def on_click(event):
            self.WP_test_execute = True

        btn = QPushButton('WP Test')
        btn.mousePressEvent = on_click
        Network_UI.Add_element(btn)

        Network_UI.Next_H_Block(stretch=1)

        self.min_slider = QSlider(1)  # QtCore.Horizontal
        self.min_slider.setMinimum(1)
        self.min_slider.setMaximum(100)
        self.min_slider.setSliderPosition(1)
        self.min_slider.mouseReleaseEvent = Network_UI.static_update_func
        self.min_slider.setToolTip('slide to cut away smallest slopes')
        Network_UI.Add_element(self.min_slider)  # , stretch=0.1

        Network_UI.Next_H_Block(stretch=1)

        self.split_slider = QSlider(1)  # QtCore.Horizontal
        self.split_slider.setMinimum(1)
        self.split_slider.setMaximum(10)
        self.split_slider.setSliderPosition(1)
        self.split_slider.mouseReleaseEvent = Network_UI.static_update_func
        self.split_slider.setToolTip('split to calculate average block')
        Network_UI.Add_element(self.split_slider)  # , stretch=0.1

        self.WP_init = False
        self.WPT_init = False

    def button_update(self, Network_UI, group):
        if self.WP_test_execute:
            self.WP_test_execute = False

            #if self.WPT_init:
            import Exploration.Network_UI.Advanced_Tabs.Helper.WP_testing as WPT
            import mrestimator as mre
            #self.WPT_init = True

            group_A_t = group[self.sum_tag, 0, 'np'].copy()  # [-1000:]
            net_A_t = np.sum(Network_UI.network[self.sum_tag], axis=0)  # np.swapaxes(, 0, 1)#

            rk, ft, (counts, bins) = WPT.branching_ratio(group_A_t, 1)
            expoffset_fit = mre.fit(rk, fitfunc=mre.f_exponential_offset)
            test1 = WPT.h_offset(ft, expoffset_fit)
            test2 = WPT.h_tau(ft, expoffset_fit)
            test3 = WPT.h_lin(rk, ft)
            print(str(test1)+' '+str(test2)+' '+str(test3))

            rk, ft, (counts, bins) = WPT.branching_ratio(net_A_t, 1)
            expoffset_fit = mre.fit(rk, fitfunc=mre.f_exponential_offset)
            test1 = WPT.h_offset(ft, expoffset_fit)
            test2 = WPT.h_tau(ft, expoffset_fit)
            test3 = WPT.h_lin(rk, ft)
            print(str(test1)+' '+str(test2)+' '+str(test3))



    def update_branching(self, Network_UI, group):

        #if not self.WP_init:
        import Exploration.Network_UI.Advanced_Tabs.Helper.WiltingPriesemann as WP
        #self.WP_init = True

        group_A_t = group[self.sum_tag, 0, 'np'].copy()[-1000:]

        net_A_t = np.sum(Network_UI.network[self.sum_tag], axis=0)#np.swapaxes(, 0, 1)#

        #print(len(group_A_t), len(net_A_t))

        k_min = self.min_slider.sliderPosition()
        k_max = min(150, len(group_A_t)-10)

        fractions = self.split_slider.sliderPosition()

        if k_max > 0:

            group_mr_A = WP.MR_estimation(group_A_t, k_min, k_max, fractions=fractions)
            self.group_scatter.setData(group_mr_A['k'], group_mr_A['r_k'])
            self.group_estimate.setData(group_mr_A['k'], group_mr_A['fitfunc'](group_mr_A['k'], *group_mr_A['p_opt']))
            self.group_m_text.setText(str(group_mr_A['branching_ratio']))


            net_mr_A = WP.MR_estimation(net_A_t, k_min, k_max, fractions=fractions)
            self.net_scatter.setData(net_mr_A['k'], net_mr_A['r_k'])
            self.net_estimate.setData(net_mr_A['k'], net_mr_A['fitfunc'](net_mr_A['k'], *net_mr_A['p_opt']))
            self.net_m_text.setText(str(net_mr_A['branching_ratio']))



    def update_avalanche_distributions(self, Network_UI, group):

        activity = group[self.sum_tag, 0, 'np']

        theta = 'half_mean'

        if theta == 'half_mean':
            theta = activity.mean() / 2.

        thresholded_activity = activity - theta
        length_act = len(activity)
        duration_list = []
        size_list = []

        duration = 0
        size = 0
        for i in range(length_act):

            # add one time step to the current avalanche
            if thresholded_activity[i] > 0:
                duration += 1
                size += int(thresholded_activity[i])

            # finish current avalanche and prepare for the next one
            elif size != 0:
                duration_list.append(duration)
                size_list.append(size)
                duration = 0
                size = 0

        T_data = np.asarray(duration_list)
        S_data = np.asarray(size_list)

        # 4. duration distribution
        T_x, T_inverse = np.unique(T_data, return_inverse=True)
        T_y_freq = np.bincount(T_inverse)
        T_y = T_y_freq / float(T_y_freq.sum())  # normalization

        if self.log:
            T_x = np.log(T_x)
            T_y = np.log(T_y)

        self.avalance_duration_curve.setData(T_x, T_y)


        S_x, S_inverse = np.unique(S_data, return_inverse=True)
        S_y_freq = np.bincount(S_inverse)
        S_y = S_y_freq / float(S_y_freq.sum())  # normalization

        if self.log:
            S_x = np.log(S_x)
            S_y = np.log(S_y)

        self.avalance_size_curve.setData(S_x, S_y)


    def update(self, Network_UI):
        if self.criticality_tab.isVisible():

            group = Network_UI.selected_neuron_group()
            n = group#for eval comand

            if self.mask_param is not None and hasattr(group, self.mask_param):
                input_mask = eval(self.compiled_param)
                not_input_mask = eval(self.inverted_compiled_param)
                mca = self.mask_color_add
            else:
                input_mask = False
                not_input_mask = True
                mca = (0, 0, 0)

            net_color_input = np.clip([group.color[0] + mca[0], group.color[1] + mca[1], group.color[2] + mca[2], 255], 0, 255)

            if hasattr(group, self.param):
                self.update_avalanche_distributions(Network_UI, group)
                self.update_branching(Network_UI, group)
                self.button_update(Network_UI, group)
