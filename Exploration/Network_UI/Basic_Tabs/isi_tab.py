from PymoNNto.Exploration.Network_UI.TabBase import *
from PymoNNto.Exploration.Visualization.Visualization_Helper import *

class isi_tab(TabBase):

    def __init__(self, title='Activity/ISI', param='output', mask_param='Input_Mask', timesteps=1000, mask_color_add=(-100, -100, -100)):
        super().__init__(title)
        self.param = param
        self.timesteps=timesteps

    def add_recorder_variables(self, neuron_group, Network_UI):
        if hasattr(neuron_group, self.param):
            Network_UI.add_recording_variable(neuron_group, self.param, timesteps=self.timesteps)
        if hasattr(neuron_group, self.param):
            self.sum_tag='np.sum('+self.param+')'
            Network_UI.add_recording_variable(neuron_group, self.sum_tag, timesteps=1000)

    def initialize(self, Network_UI):
        self.isi_tab = Network_UI.add_tab(title=self.title) #Network_UI.Next_Tab(self.title)

        self.neuron_isi_plt = Network_UI.tab.add_plot(title='selected inter spike interval hist', x_label='ISI', y_label='Frequency')
        self.net_isi_plt = Network_UI.tab.add_plot(title='network inter spike interval hist', x_label='ISI', y_label='Frequency')

        Network_UI.tab.add_row()
        self.neuron_isi_bin_slider = QSlider(1)  # QtCore.Horizontal
        self.neuron_isi_bin_slider.setMinimum(1)
        self.neuron_isi_bin_slider.setMaximum(100)
        self.neuron_isi_bin_slider.setSliderPosition(10)
        self.neuron_isi_bin_slider.mouseReleaseEvent = Network_UI.static_update_func
        self.neuron_isi_bin_slider.setToolTip('slide to change bin count')
        Network_UI.tab.add_widget(self.neuron_isi_bin_slider)  # , stretch=0.1

        self.net_isi_bin_slider = QSlider(1)  # QtCore.Horizontal
        self.net_isi_bin_slider.setMinimum(1)
        self.net_isi_bin_slider.setMaximum(100)
        self.net_isi_bin_slider.setSliderPosition(10)
        self.net_isi_bin_slider.mouseReleaseEvent = Network_UI.static_update_func
        self.net_isi_bin_slider.setToolTip('slide to change bin count')
        Network_UI.tab.add_widget(self.net_isi_bin_slider)

        Network_UI.tab.add_row()
        Network_UI.tab.add_widget(QLabel(''))
        self.net_isi_cb = Network_UI.tab.add_widget(QCheckBox('Compute network isi'))

        Network_UI.tab.add_row()
        self.neuron_avg_act_label = Network_UI.tab.add_widget(QLabel('-'))
        self.net_avg_hist_plt = Network_UI.tab.add_plot(title='network avg activities', x_label='average activity', y_label='Frequency')

        Network_UI.tab.add_row()

        Network_UI.tab.add_widget(QLabel(''))

        self.net_avg_bin_slider = QSlider(1)  # QtCore.Horizontal
        self.net_avg_bin_slider.setMinimum(1)
        self.net_avg_bin_slider.setMaximum(100)
        self.net_avg_bin_slider.setSliderPosition(10)
        self.net_avg_bin_slider.mouseReleaseEvent = Network_UI.static_update_func
        self.net_avg_bin_slider.setToolTip('slide to change bin count')
        Network_UI.tab.add_widget(self.net_avg_bin_slider)

        Network_UI.tab.add_row(stretch=1)

        Network_UI.tab.add_widget(QLabel('interval length: '+str(self.timesteps)+' steps'))


    def update_ISI(self, Network_UI, group, input_mask, not_input_mask, net_color_input):

        act_data = group[self.param, 0, 'np'][-self.timesteps:, :]

        self.neuron_isi_plt.clear()
        sel_bins = self.neuron_isi_bin_slider.sliderPosition()

        sel_hist_data = []

        for i in Network_UI.selected_neuron_ids():
            sel_hist_data += SpikeTrain_ISI(act_data[:, i])
        y, x = np.histogram(sel_hist_data, bins=sel_bins)

        curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=Network_UI.neuron_select_color)
        self.neuron_isi_plt.addItem(curve)


        self.net_isi_plt.clear()
        if self.net_isi_cb.isChecked():
            net_bins = self.net_isi_bin_slider.sliderPosition()
            net_hist_data = []
            for i in range(act_data.shape[1]):
                net_hist_data+=SpikeTrain_ISI(act_data[:,i])
            y, x = np.histogram(net_hist_data, bins=net_bins)
            curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=group.color)
            self.net_isi_plt.addItem(curve)


    def update_Mean_Activity(self, Network_UI, group, input_mask, not_input_mask, net_color_input):
        net_bins = self.net_avg_bin_slider.sliderPosition()

        avg_acts = np.mean(group[self.param, 0, 'np'][-self.timesteps:, :], axis=0)

        color_str=('#%02x%02x%02x'% Network_UI.neuron_select_color[0:3]).upper()
        self.neuron_avg_act_label.setText('Selected neuron average spike rate:<br><font color='+color_str+'>'+str(avg_acts[Network_UI.selected_neuron_id()])+'</font>')

        self.net_avg_hist_plt.clear()
        y, x = np.histogram(avg_acts[not_input_mask], bins=net_bins)
        curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=group.color)
        self.net_avg_hist_plt.addItem(curve)


    def update(self, Network_UI):
        if self.isi_tab.isVisible():

            group = Network_UI.selected_neuron_group()
            n = group#for eval comand

            input_mask = False
            not_input_mask = True
            mca = (0, 0, 0)

            net_color_input = np.clip([group.color[0] + mca[0], group.color[1] + mca[1], group.color[2] + mca[2], 255], 0, 255)

            if hasattr(group, self.param):
                self.update_ISI(Network_UI, group, input_mask, not_input_mask, net_color_input)
                self.update_Mean_Activity(Network_UI, group, input_mask, not_input_mask, net_color_input)
