from PymoNNto.Exploration.Network_UI.TabBase import *

class weight_tab(TabBase):

    def __init__(self, title='Weights', weight_attrs=['W']):
        super().__init__(title)
        self.weight_attrs = weight_attrs

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def initialize(self, Network_UI):
        self.weight_tab = Network_UI.add_tab(title=self.title)
        self.main_plot = Network_UI.tab.add_plot()

        Network_UI.tab.add_row()

        self.select_mode = QComboBox()
        self.select_mode.addItems(['selected neuron', 'all'])
        self.select_mode.setCurrentIndex(0)
        Network_UI.tab.add_widget(self.select_mode, stretch=1)

        self.select_aff_eff = QComboBox()
        self.select_aff_eff.addItems(['afferent', 'efferent'])
        self.select_aff_eff.setCurrentIndex(0)
        Network_UI.tab.add_widget(self.select_aff_eff, stretch=1)

        self.select_min_box = QComboBox()
        self.select_min_box.addItems(['global min', 'single min', '0'])
        self.select_min_box.setCurrentIndex(1)
        Network_UI.tab.add_widget(self.select_min_box, stretch=1)

        self.select_max_box = QComboBox()
        self.select_max_box.addItems(['global max', 'single max', '1'])
        self.select_max_box.setCurrentIndex(1)
        Network_UI.tab.add_widget(self.select_max_box, stretch=1)


    def update(self, Network_UI):
        if self.weight_tab.isVisible():
            group = Network_UI.selected_neuron_group()
            selected = Network_UI.selected_neuron_id()

            self.main_plot.clear()

            afferent=self.select_aff_eff.currentText() == 'afferent'
            single = self.select_mode.currentText() != 'all'
            max_mode = self.select_max_box.currentText()
            min_mode = self.select_min_box.currentText()

            c = 0
            syns = []
            syn_tags=[]
            max_s = []
            min_s = []

            if afferent:
                for s in group.synapses(afferent):
                    w = s.ignore_transpose_mode(s.W)

                    if single:
                        data = np.rot90(w[selected].reshape(s.src.height, s.src.width), 3)
                    else:
                        data = w
                    syns.append(data)
                    syn_tags.append(s.tags)
            else:
                for s in group.efferent_synapses['All']:
                    w = s.ignore_transpose_mode(s.W)

                    if single:
                        data = np.rot90(w[:, selected].reshape(s.dst.height, s.dst.width), 3)
                    else:
                        data = w
                    syns.append(data)
                    syn_tags.append(s.tags)

            for data in syns:
                max_s.append(np.max(data))
                min_s.append(np.min(data))

            max_s = np.array(max_s)
            min_s = np.array(min_s)

            if len(max_s) > 0:
                if max_mode == 'global max':
                    max_s[:] = np.max(max_s)
                elif max_mode == 'single max':
                    max_s[:] = max_s[:]
                else:
                    max_s[:] = float(max_mode)

                if min_mode == 'global min':
                    min_s[:] = np.max(min_s)
                elif min_mode == 'single min':
                    min_s[:] = min_s[:]
                else:
                    min_s[:] = float(min_mode)

            for data, ma, mi, tags in zip(syns, max_s, min_s, syn_tags):
                image = self.main_plot.add_image()
                image.setImage(data, levels=(mi, ma))
                text = self.main_plot.add_text(str(tags))

                text.setPos(0, c+10)
                image.setRect(0, c-data.shape[1], data.shape[0], data.shape[1])
                c -= data.shape[1] + 20
