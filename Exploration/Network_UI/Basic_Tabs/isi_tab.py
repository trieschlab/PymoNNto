from PymoNNto.Exploration.Network_UI.TabBase import *
from PymoNNto.Exploration.Visualization.Visualization_Helper import *

class isi_tab(TabBase):

    def __init__(self, title='Activity/ISI', param='output', mask_param='Input_Mask', timesteps=1000, mask_color_add=(-100, -100, -100)):
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
            Network_UI.add_recording_variable(neuron_group, 'n.' + self.param, timesteps=self.timesteps)
        if hasattr(neuron_group, self.param):
            self.sum_tag='np.sum(n.'+self.param+')'
            Network_UI.add_recording_variable(neuron_group, self.sum_tag, timesteps=1000)

    def initialize(self, Network_UI):
        self.isi_tab = Network_UI.Next_Tab(self.title)

        _, self.neuron_isi_plt = Network_UI.Add_plot_curve('neuron inter spike interval hist', True, False, legend=False, x_label='ISI', y_label='Frequency')
        _, self.net_isi_plt = Network_UI.Add_plot_curve('network inter spike interval hist', True, False, legend=False, x_label='ISI', y_label='Frequency')
        if self.mask_param is not None:
            _, self.input_isi_plt = Network_UI.Add_plot_curve('input inter spike interval hist', True, False, legend=False, x_label='ISI', y_label='Frequency')

        Network_UI.Next_H_Block()
        self.neuron_isi_bin_slider = QSlider(1)  # QtCore.Horizontal
        self.neuron_isi_bin_slider.setMinimum(1)
        self.neuron_isi_bin_slider.setMaximum(100)
        self.neuron_isi_bin_slider.setSliderPosition(10)
        self.neuron_isi_bin_slider.mouseReleaseEvent = Network_UI.static_update_func
        self.neuron_isi_bin_slider.setToolTip('slide to change bin count')
        Network_UI.Add_element(self.neuron_isi_bin_slider)  # , stretch=0.1

        self.net_isi_bin_slider = QSlider(1)  # QtCore.Horizontal
        self.net_isi_bin_slider.setMinimum(1)
        self.net_isi_bin_slider.setMaximum(100)
        self.net_isi_bin_slider.setSliderPosition(10)
        self.net_isi_bin_slider.mouseReleaseEvent = Network_UI.static_update_func
        self.net_isi_bin_slider.setToolTip('slide to change bin count')
        Network_UI.Add_element(self.net_isi_bin_slider)  # , stretch=0.1


        if self.mask_param is not None:
            self.input_isi_bin_slider = QSlider(1)  # QtCore.Horizontal
            self.input_isi_bin_slider.setMinimum(1)
            self.input_isi_bin_slider.setMaximum(100)
            self.input_isi_bin_slider.setSliderPosition(10)
            self.input_isi_bin_slider.mouseReleaseEvent = Network_UI.static_update_func
            self.input_isi_bin_slider.setToolTip('slide to change bin count')
            Network_UI.Add_element(self.input_isi_bin_slider)  # , stretch=0.1

        Network_UI.Next_H_Block()
        Network_UI.Add_element(QLabel(''))
        self.net_isi_cb = Network_UI.Add_element(QCheckBox('Compute network isi'))
        #self.net_isi_cb.setChecked(True)
        if self.mask_param is not None:
            self.input_isi_cb = Network_UI.Add_element(QCheckBox('Compute input isi'))
            #self.input_isi_cb.setChecked(True)

        Network_UI.Next_H_Block()
        self.neuron_avg_act_label = Network_UI.Add_element(QLabel('-'))
        _, self.net_avg_hist_plt = Network_UI.Add_plot_curve('network avg activities', True, False, legend=False, x_label='average activity', y_label='Frequency')
        if self.mask_param is not None:
            _, self.input_avg_hist_plt = Network_UI.Add_plot_curve('input avg activities', True, False, legend=False, x_label='average activity', y_label='Frequency')

        Network_UI.Next_H_Block()

        Network_UI.Add_element(QLabel(''))

        self.net_avg_bin_slider = QSlider(1)  # QtCore.Horizontal
        self.net_avg_bin_slider.setMinimum(1)
        self.net_avg_bin_slider.setMaximum(100)
        self.net_avg_bin_slider.setSliderPosition(10)
        self.net_avg_bin_slider.mouseReleaseEvent = Network_UI.static_update_func
        self.net_avg_bin_slider.setToolTip('slide to change bin count')
        Network_UI.Add_element(self.net_avg_bin_slider)  # , stretch=0.1

        if self.mask_param is not None:
            self.input_avg_bin_slider = QSlider(1)  # QtCore.Horizontal
            self.input_avg_bin_slider.setMinimum(1)
            self.input_avg_bin_slider.setMaximum(100)
            self.input_avg_bin_slider.setSliderPosition(10)
            self.input_avg_bin_slider.mouseReleaseEvent = Network_UI.static_update_func
            self.input_avg_bin_slider.setToolTip('slide to change bin count')
            Network_UI.Add_element(self.input_avg_bin_slider)  # , stretch=0.1

        Network_UI.Next_H_Block(stretch=1)

        Network_UI.Add_element(QLabel('interval length: '+str(self.timesteps)+' steps'))





    def update_ISI(self, Network_UI, group, input_mask, not_input_mask, net_color_input):

        neuron_bins = self.neuron_isi_bin_slider.sliderPosition()
        act_data = group['n.' + self.param, 0, 'np'][-self.timesteps:,:]

        self.neuron_isi_plt.clear()
        y, x = np.histogram(SpikeTrain_ISI(act_data[-self.timesteps:, Network_UI.selected_neuron_id()]), bins=neuron_bins)
        curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=Network_UI.neuron_select_color)
        self.neuron_isi_plt.addItem(curve)

        self.net_isi_plt.clear()
        if self.net_isi_cb.isChecked():
            if not_input_mask is True:
                net_act_data = act_data
            else:
                net_act_data=act_data[:,not_input_mask]
            net_bins = self.net_isi_bin_slider.sliderPosition()
            net_hist_data = []
            for i in range(net_act_data.shape[1]):
                net_hist_data+=SpikeTrain_ISI(net_act_data[:,i])
            y, x = np.histogram(net_hist_data, bins=net_bins)
            curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=group.color)
            self.net_isi_plt.addItem(curve)

        if self.mask_param is not None:
            self.input_isi_plt.clear()
            if input_mask is not False and self.input_isi_cb.isChecked():
                input_act_data = act_data[:, input_mask]
                input_bins = self.input_isi_bin_slider.sliderPosition()
                input_hist_data = []
                for i in range(input_act_data.shape[1]):
                    input_hist_data+=SpikeTrain_ISI(input_act_data[:,i])
                y, x = np.histogram(input_hist_data, bins=input_bins)
                curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=net_color_input)
                self.input_isi_plt.addItem(curve)

    def update_Mean_Activity(self, Network_UI, group, input_mask, not_input_mask, net_color_input):
        #rec = Network_UI.rec(group, self.timesteps)

        net_bins = self.net_avg_bin_slider.sliderPosition()

        avg_acts = np.mean(group['n.' + self.param, 0, 'np'][-self.timesteps:, :], axis=0)

        color_str=('#%02x%02x%02x'% Network_UI.neuron_select_color[0:3]).upper()
        self.neuron_avg_act_label.setText('Selected neuron average spike rate:<br><font color='+color_str+'>'+str(avg_acts[Network_UI.selected_neuron_id()])+'</font>')

        self.net_avg_hist_plt.clear()
        y, x = np.histogram(avg_acts[not_input_mask], bins=net_bins)
        curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=group.color)
        self.net_avg_hist_plt.addItem(curve)

        if self.mask_param is not None:
            self.input_avg_hist_plt.clear()
            if input_mask is not False:
                input_bins = self.input_avg_bin_slider.sliderPosition()
                y, x = np.histogram(avg_acts[input_mask], bins=input_bins)
                curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=net_color_input)  # todo:make faster!
                self.input_avg_hist_plt.addItem(curve)  # todo:make faster!

    def update(self, Network_UI):
        if self.isi_tab.isVisible():

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
                self.update_ISI(Network_UI, group, input_mask, not_input_mask, net_color_input)
                self.update_Mean_Activity(Network_UI, group, input_mask, not_input_mask, net_color_input)
