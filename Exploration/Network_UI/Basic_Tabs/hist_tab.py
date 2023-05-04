from PymoNNto.Exploration.Network_UI.TabBase import *

class hist_tab(TabBase):

    def __init__(self, weight_attr='W', title='Weight Dist.', timesteps=1000, mask_param='Input_Mask', mask_color_add=(-100, -100, -100)):#mask_param=None #
        super().__init__(title)
        self.weight_attr = weight_attr
        self.timesteps = timesteps

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def initialize(self, Network_UI):
        self.additionaltab = Network_UI.add_tab(title=self.title)

        self.weight_hist_plots = {}
        self.net_weight_hist_plots = {}

        for i,transmitter in enumerate(Network_UI.transmitters):
            if i>0:
                Network_UI.tab.add_row()

            self.weight_hist_plots[transmitter] = Network_UI.tab.add_plot(title=transmitter + ' selected weight hist', x_label=transmitter + ' synapse size', y_label='Frequency')
            self.net_weight_hist_plots[transmitter] = Network_UI.tab.add_plot(title=transmitter + ' network weight hist', x_label=transmitter + ' synapse size', y_label='Frequency')

        Network_UI.tab.add_row()
        #self.min_hist_slider = QSlider(1)  # QtCore.Horizontal
        #self.min_hist_slider.setMinimum(-1)
        #self.min_hist_slider.setMaximum(10)
        #self.min_hist_slider.setSliderPosition(0)
        #self.min_hist_slider.mouseReleaseEvent = Network_UI.static_update_func
        #self.min_hist_slider.setToolTip('slide to cut away smallest weights')
        #Network_UI.tab.add_widget(self.min_hist_slider)  # , stretch=0.1

        Network_UI.tab.add_widget(QLabel('min: '))
        self.qsb_min = QDoubleSpinBox()
        self.qsb_min.setDecimals(5)
        self.qsb_min.setValue(0.0)
        self.qsb_min.setSingleStep(0.00001)
        Network_UI.tab.add_widget(self.qsb_min)

        Network_UI.tab.add_widget(QLabel('max: '))
        self.qsb_max = QDoubleSpinBox()
        self.qsb_max.setDecimals(5)
        self.qsb_max.setValue(1.0)
        self.qsb_max.setSingleStep(0.00001)
        Network_UI.tab.add_widget(self.qsb_max)

        #Network_UI.tab.add_row()
        Network_UI.tab.add_widget(QLabel('bins: '))
        self.bin_slider = QSlider(1)  # QtCore.Horizontal
        self.bin_slider.setMinimum(1)
        self.bin_slider.setMaximum(100)
        self.bin_slider.setSliderPosition(50)
        self.bin_slider.mouseReleaseEvent = Network_UI.static_update_func
        self.bin_slider.setToolTip('slide to change bin count')
        Network_UI.tab.add_widget(self.bin_slider)  # , stretch=0.1

    def update_Synapse_Historgrams(self, Network_UI, group, net_color_input):
        #msl = self.min_hist_slider.sliderPosition() * 0.001

        min_weight = self.qsb_min.value()
        max_weight = self.qsb_max.value()

        bins = self.bin_slider.sliderPosition()

        for transmitter in Network_UI.transmitters:

            self.net_weight_hist_plots[transmitter].clear()
            self.weight_hist_plots[transmitter].clear()

            glu_syns = group.synapses(afferent, transmitter)
            if len(glu_syns) > 0:

                GLU_syn_list = get_combined_syn_mats(glu_syns, None, self.weight_attr)
                GLU_syn_list_en = get_combined_syn_mats(glu_syns, None, "enabled")
                if len(GLU_syn_list) > 0:
                    GLU_syn = GLU_syn_list[list(GLU_syn_list.keys())[0]]
                    en_mask = GLU_syn_list_en[list(GLU_syn_list_en.keys())[0]].astype(bool)*(GLU_syn > min_weight)*(GLU_syn < max_weight)#GLU_syn > msl

                    self.net_weight_hist_plots[transmitter].clear()
                    y, x = np.histogram(GLU_syn[en_mask], bins=bins)#[GLU_syn[not_input_mask] > msl]
                    curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=group.color)
                    self.net_weight_hist_plots[transmitter].addItem(curve)

                    self.weight_hist_plots[transmitter].clear()
                    y, x = np.histogram(GLU_syn[Network_UI.selected_neuron_mask()][en_mask[Network_UI.selected_neuron_mask()]], bins=bins)#[selected_neuron_GLU_syn > msl]
                    curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=Network_UI.neuron_select_color)
                    self.weight_hist_plots[transmitter].addItem(curve)


    def update(self, Network_UI):
        if self.additionaltab.isVisible():

            group = Network_UI.selected_neuron_group()
            n=group#for eval comand

            mca = (0,0,0)

            net_color_input = np.clip([group.color[0] + mca[0], group.color[1] + mca[1], group.color[2] + mca[2], 255], 0, 255)

            self.update_Synapse_Historgrams(Network_UI, group, net_color_input)
