from PymoNNto.Exploration.Network_UI.TabBase import *
from PymoNNto.NetworkBehaviour.Recorder.Recorder import *

class individual_weight_tab(TabBase):

    def __init__(self, title='Ind Weights', weight_attr='W'):
        super().__init__(title)
        self.weight_attr = weight_attr

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def initialize(self, Network_UI):
        self.individual_weight_tab = Network_UI.Next_Tab(self.title)

        self.plot = Network_UI.Add_plot('Neuron Weights', stretch = 8)

        self.rec_name=self.title + '_rec'
        self.Network_UI=Network_UI

        self.current_ng=None
        self.neuron_index=-1
        self.my_syn_rec=None

        self.key=''

        self.listWidget = Network_UI.Add_element(QListWidget())

        Network_UI.Next_H_Block()

        self.min_w_slider = QSlider(1)  # QtCore.Horizontal
        self.min_w_slider.setMinimum(-1)
        self.min_w_slider.setMaximum(100)
        self.min_w_slider.setSliderPosition(-1)
        self.min_w_slider.setToolTip('slide to cut away x% of smallest weights')
        self.min_w_slider.mouseReleaseEvent = Network_UI.static_update_func
        Network_UI.Add_element(self.min_w_slider)


    def start_rec(self, group):

        if self.current_ng is not None and (self.neuron_index != self.Network_UI.selected_neuron_id() or self.current_ng != group):

            for s in self.current_ng.afferent_synapses["All"]:
                s.UI_recorder = None
                s.cb = None
                self.Network_UI.network.remove_behaviours_from_object(s, tags=[self.key])

            self.listWidget.clear()
            self.plot.clear()

            self.current_ng = None
            self.neuron_index = -1
            print('removed')

        if self.current_ng is None:

            self.current_ng = group
            self.neuron_index = self.Network_UI.selected_neuron_id()

            print('started')
            self.plot.clear()

            self.key = 's.'+self.weight_attr+'['+str(self.neuron_index)+']'

            self.checkboxes={}
            self.listWidget.clear()

            for s in group.afferent_synapses["All"]:
                s.UI_recorder = Recorder([self.key, 's.iteration'], tag=self.rec_name, gapwidth=10, save_as_numpy=True)
                s.add_behaviour(10001, s.UI_recorder)
                #self.Network_UI.network.add_behaviours_to_object({10001: s.UI_recorder}, s)

                s.UI_curves = []
                syn_data = eval(self.key)

                s.cb = QListWidgetItem(str(s.tags[0]))
                s.cb.setCheckState(2)
                self.listWidget.addItem(s.cb)

                for i in range(len(syn_data)):
                    if (type(s.enabled) is bool and s.enabled) or s.enabled[self.neuron_index, i]:
                        color = (s.src.color[0], s.src.color[1], s.src.color[2], 255)
                        curve = pg.PlotCurveItem([], pen=color)  # pen=colors[i%len(colors)]
                        curve.index = i
                        self.plot.addItem(curve)
                        s.UI_curves.append(curve)


    def update(self, Network_UI):

        if self.individual_weight_tab.isVisible():

            group = Network_UI.selected_neuron_group()
            self.start_rec(group)

            for s in self.current_ng.afferent_synapses["All"]:
                if not s.UI_recorder.behaviour_enabled:
                    s.UI_recorder.behaviour_enabled = True
                    print('recorder started')
                if s.cb.checkState() == 2:
                    if s.UI_recorder.is_new_data_available():
                        x_data = s.UI_recorder['s.iteration', 0]
                        y_data = s.UI_recorder[self.key, 0]

                        if len(x_data) > 0 and len(y_data) > 0:
                            for curve in s.UI_curves:
                                curve.setData(x_data, y_data[:, curve.index])
        else:
            if self.current_ng is not None:
                for s in self.current_ng.afferent_synapses["All"]:
                    if s.UI_recorder.behaviour_enabled:
                        s.UI_recorder.behaviour_enabled=False
                        print('recorder paused')
