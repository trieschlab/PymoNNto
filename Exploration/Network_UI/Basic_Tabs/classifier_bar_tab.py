from PymoNNto.Exploration.Network_UI.TabBase import *
from PymoNNto.Exploration.Visualization.Visualization_Helper import *
from PymoNNto.Exploration.Network_UI.Network_UI import *

class classifier_bar_tab(TabBase):


    def initialize(self, Network_UI):
        self.cluster_bar_tab = Network_UI.add_tab(title='Cluster')
        self.plot = Network_UI.tab.add_plot('cluster sizes')
        self.bgi = pg.BarGraphItem(x=[], height=[], width=0.6, brush='r')
        self.plot.addItem(self.bgi)

        self.class_id_positions = {}


        def mouseClickEvent(event):
            click_y_pos = np.round(event.pos().y())
            for c in self.class_id_positions:
                y_pos = self.class_id_positions[c]
                if click_y_pos == y_pos:
                    Network_UI.select_neuron_class(self.current_group, c)

        self.bgi.mouseClickEvent = mouseClickEvent

        Network_UI.tab.add_row()

        self.class_tag_dict = None

        def on_new_label_selected(group, module, key, labels):
            generator = group.network['Text_Generator', 0]
            if hasattr(group, 'classification') and module is not None and generator is not None:
                self.class_tag_dict = module.get_class_labels(key, group.classification, generator)

        self.comboBox = Network_UI.tab.add_widget(Analytics_Results_Select_ComboBox(Network_UI.network.NeuronGroups[0], tag='labeler', first_entry='none'))
        self.comboBox.on_update_func = on_new_label_selected


    def update(self, Network_UI):
        if self.cluster_bar_tab.isVisible():
            self.current_group = Network_UI.selected_neuron_group()
            if hasattr(self.current_group, 'classification'):
                selected_classes = Network_UI.selected_class_ids()

                idx = []
                num = []
                col = []
                labels = []
                cd = self.current_group['Neuron_Classification_Colorizer', 0].get_class_color_dict(self.current_group.classification, format='[r,g,b]')#.get_color_list(group.classification, format='[r,g,b]'))

                for i, c in enumerate(np.unique(self.current_group.classification)):

                    idx.append(i)
                    num.append(np.sum(self.current_group.classification == c))

                    if c in selected_classes:
                        col.append((0, 255, 0))
                    else:
                        col.append(cd[c])

                    if self.class_tag_dict is not None and c in self.class_tag_dict:
                        labels.append(self.class_tag_dict[c])

                sort_indx = np.argsort(-np.array(num))


                for i, c in enumerate(np.unique(self.current_group.classification)[sort_indx]):
                    self.class_id_positions[c] = i

                self.bgi.setOpts(x=np.array(num)[sort_indx] / 2, y=idx, height=0.6, width=np.array(num)[sort_indx], brushes=np.array(col)[sort_indx])

                if len(sort_indx)==len(labels):
                    labels = [(i, l) for i, l in enumerate(np.array(labels)[sort_indx])]

                self.plot.showAxis('left')
                ax = self.plot.getAxis('left')
                ax.setTickFont(QFont("Courier"))
                ax.setWidth(100)
                ax.setTicks([labels])
