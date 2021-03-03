'''
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

        self.listWidget = QListWidget()
        Network_UI.Add_element(self.listWidget)

        Network_UI.Next_H_Block()

        self.min_w_slider = QSlider(1)  # QtCore.Horizontal
        self.min_w_slider.setMinimum(-1)
        self.min_w_slider.setMaximum(100)
        self.min_w_slider.setSliderPosition(-1)
        self.min_w_slider.setToolTip('slide to cut away x% of smallest weights')
        self.min_w_slider.mouseReleaseEvent = Network_UI.static_update_func
        Network_UI.Add_element(self.min_w_slider)


    def start_rec(self, group):

        # self.key = 'np.concatenate([s.W[:,np.where(s.dst.id=='+str(self.neuron_index)+')[0]][s.enabled[:,np.where(s.dst.id=='+str(self.neuron_index)+')[0]]] for s in n.afferent_synapses["All"]])'
        # self.my_syn_rec = Recorder([self.key], tag=self.rec_name)

        if len(group[self.rec_name]) == 0 or self.Network_UI.neuron_select_id != self.neuron_index:

            if self.current_ng is not None and len(self.current_ng[self.rec_name]) > 0:
                self.Network_UI.network.remove_behaviours_from_object(self.current_ng, tags=[self.rec_name])
                self.my_syn_rec=None
                print('stop')

            #if self.my_syn_rec is not None:
            #    self.Network_UI.network.remove_behaviours_from_neuron_groups([self.current_ng], tags=[self.rec_name])
            #        print('stop')

            print('started', group)
            self.plot.clear()

            self.neuron_index = self.Network_UI.neuron_select_id

            self.curves = {}
            self.keys = []
            self.checkboxes={}
            self.listWidget.clear()
            for i, s in enumerate(group.afferent_synapses["All"]):
                new_id = np.where(s.dst.id == self.neuron_index)[0]
                if len(new_id) > 0:# and hasattr(s, self.weight_attr): #TODO:
                    new_id = new_id[0]

                    weight = eval('s.' + self.weight_attr)

                    if type(s.enabled)==bool:
                        syn_count = len(weight[new_id])
                    else:
                        syn_count = len(weight[new_id,:][s.enabled[new_id,:]])

                    #print(weight.shape, new_id, enabled)
                    #syn_count = len(weight[new_id][enabled])#,:
                    if syn_count > 0:

                        color = (s.src.color[0], s.src.color[1], s.src.color[2], 255)

                        if type(group.afferent_synapses["All"][i].enabled) == bool:
                            enabled_string = 'True'
                        else:
                            enabled_string='n.afferent_synapses["All"]['+str(i)+'].enabled['+str(new_id)+',:]'


                        k = 'n.afferent_synapses["All"]['+str(i)+'].W['+str(new_id)+',:]['+enabled_string+']'
                        self.curves[k] = []
                        self.keys.append(k)

                        self.checkboxes[k] = QListWidgetItem(str(s.src.tags[0]))
                        self.checkboxes[k].setCheckState(2)
                        self.listWidget.addItem(self.checkboxes[k])

                        for i in range(syn_count):
                            curve = pg.PlotCurveItem([], pen=color)  # pen=colors[i%len(colors)]
                            self.plot.addItem(curve)
                            self.curves[k].append(curve)

            self.my_syn_rec = Recorder(self.keys + ['n.iteration'], tag=self.rec_name, gapwidth=10)
            self.Network_UI.network.add_behaviours_to_object({10001: self.my_syn_rec}, group)
            self.current_ng = group


            #size = len(np.concatenate([s.W[:, new_indx][s.enabled[:, new_indx]] for s in group.afferent_synapses["All"]]))
            #print(size)

            return False
        else:
            return True

    def update(self, Network_UI):

        if self.individual_weight_tab.isVisible():
            if len(Network_UI.network[Network_UI.neuron_select_group]) > 0:

                group = Network_UI.network[Network_UI.neuron_select_group, 0]

                if (self.start_rec(group) and self.my_syn_rec.is_new_data_available()) or self.my_syn_rec.active == False:

                    if self.my_syn_rec.active==False:
                        print('continue')
                        self.my_syn_rec.active=True

                    x_data=self.my_syn_rec['n.iteration', 0, 'np']

                    for k in self.keys:

                        neuron_data = self.my_syn_rec[k, 0, 'np']

                        #print(neuron_data)

                        if len(neuron_data)>0:
                            mws = np.max(neuron_data)/100*self.min_w_slider.sliderPosition()

                            for i, curve in enumerate(self.curves[k]):
                                if self.checkboxes[k].checkState() == 2:
                                    d=neuron_data[:, i]
                                    #if d[-1]>=mws:
                                    #print(x_data.shape,d.shape)
                                    curve.setData(x_data, d)
                                    #else:
                                    #    curve.clear()
                                else:
                                    curve.clear()
        else:
            if self.my_syn_rec is not None and self.my_syn_rec.active==True:
                print('paused')
                self.my_syn_rec.active=False
'''


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

        #if self.current_ng is not None and len(self.current_ng[self.rec_name]) > 0 and self.Network_UI.neuron_select_id != self.neuron_index:
        #    self.Network_UI.network.remove_behaviours_from_object(self.current_ng, tags=[self.rec_name])
        #    self.my_syn_rec = None
        #    print('stop')

        if self.current_ng is not None and (self.neuron_index != self.Network_UI.neuron_select_id or self.current_ng != group):

            for s in self.current_ng.afferent_synapses["All"]:
                s.UI_recorder = None
                s.cb = None
                self.Network_UI.network.remove_behaviours_from_object(s, tags=[self.key])

            self.listWidget.clear()
            self.plot.clear()

            self.current_ng = None
            self.neuron_index = -1
            print('removed')

        if self.current_ng is None:#len(self.Network_UI.network[self.key]) == 0:

            self.current_ng = group
            self.neuron_index = self.Network_UI.neuron_select_id

            # self.key = 'np.concatenate([s.W[:,np.where(s.dst.id=='+str(self.neuron_index)+')[0]][s.enabled[:,np.where(s.dst.id=='+str(self.neuron_index)+')[0]]] for s in n.afferent_synapses["All"]])'
            # self.my_syn_rec = Recorder([self.key], tag=self.rec_name)


            #if self.my_syn_rec is not None:
            #    self.Network_UI.network.remove_behaviours_from_neuron_groups([self.current_ng], tags=[self.rec_name])
            #        print('stop')

            print('started')
            self.plot.clear()

            self.key = 's.'+self.weight_attr+'['+str(self.neuron_index)+']'

            self.checkboxes={}
            self.listWidget.clear()

            for s in group.afferent_synapses["All"]:
                s.UI_recorder = Recorder([self.key, 's.iteration'], tag=self.rec_name, gapwidth=10, save_as_numpy=True)
                self.Network_UI.network.add_behaviours_to_object({10001: s.UI_recorder}, s)

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


                #self.curves[k] = []
                #self.keys.append(k)

                #self.checkboxes[k] = QListWidgetItem(str(s.src.tags[0]))
                #self.checkboxes[k].setCheckState(2)
                #self.listWidget.addItem(self.checkboxes[k])

                #for i in range(syn_count):


                '''
                new_id = np.where(s.dst.id == self.neuron_index)[0]
                if len(new_id) > 0:# and hasattr(s, self.weight_attr): #TODO:
                    new_id = new_id[0]

                    weight = eval('s.' + self.weight_attr)

                    if type(s.enabled)==bool:
                        syn_count = len(weight[new_id])
                    else:
                        syn_count = len(weight[new_id,:][s.enabled[new_id,:]])

                    #print(weight.shape, new_id, enabled)
                    #syn_count = len(weight[new_id][enabled])#,:
                    if syn_count > 0:

                        color = (s.src.color[0], s.src.color[1], s.src.color[2], 255)

                        if type(group.afferent_synapses["All"][i].enabled) == bool:
                            enabled_string = 'True'
                        else:
                            enabled_string='n.afferent_synapses["All"]['+str(i)+'].enabled['+str(new_id)+',:]'


                        k = 'n.afferent_synapses["All"]['+str(i)+'].W['+str(new_id)+',:]['+enabled_string+']'
                        self.curves[k] = []
                        self.keys.append(k)

                        self.checkboxes[k] = QListWidgetItem(str(s.src.tags[0]))
                        self.checkboxes[k].setCheckState(2)
                        self.listWidget.addItem(self.checkboxes[k])

                        for i in range(syn_count):
                            curve = pg.PlotCurveItem([], pen=color)  # pen=colors[i%len(colors)]
                            self.plot.addItem(curve)
                            self.curves[k].append(curve)
                '''

            #self.my_syn_rec = Recorder(self.keys + ['n.iteration'], tag=self.rec_name, gapwidth=10)
            #self.Network_UI.network.add_behaviours_to_object({10001: self.my_syn_rec}, group)
            #self.current_ng = group


            #size = len(np.concatenate([s.W[:, new_indx][s.enabled[:, new_indx]] for s in group.afferent_synapses["All"]]))
            #print(size)


    def update(self, Network_UI):

        if self.individual_weight_tab.isVisible():
            if len(Network_UI.network[Network_UI.neuron_select_group]) > 0:

                group = Network_UI.network[Network_UI.neuron_select_group, 0]
                self.start_rec(group)

                for s in self.current_ng.afferent_synapses["All"]:
                    if not s.UI_recorder.active:
                        s.UI_recorder.active = True
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
                    if s.UI_recorder.active:
                        s.UI_recorder.active=False
                        print('recorder paused')
