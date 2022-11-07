from PymoNNto.Exploration.Network_UI.Network_UI import *
from PymoNNto.Exploration.Network_UI.TabBase import *
import scipy.cluster.hierarchy as sch
import matplotlib.pyplot as plt

def generatePgColormap(cm_name):
    pltMap = plt.get_cmap(cm_name)
    colors = pltMap.colors
    colors = [c + [1.] for c in colors]
    positions = np.linspace(0, 1, len(colors))
    pgMap = pg.ColorMap(positions, np.array(colors)*255.0)
    return pgMap

class similarity_matrix_tab(TabBase):

    def __init__(self, title='similarity'):
        super().__init__(title)

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def update_labels(self):
        labels = self.left_axis_cb.get_selected_result()
        if labels is not None:
            if self.current_label_resort is not None:
                labels = list(np.flip(np.array(labels)[self.current_label_resort]))
            labels = [(0.5 + i, l) for i, l in enumerate(labels)]
            self.plot.showAxis('left')
            ax = self.plot.getAxis('left')
            ax.setTickFont(QFont("Courier"))
            ax.setWidth(100)
            ax.setTicks([labels])

        labels = self.right_axis_cb.get_selected_result()
        if labels is not None:
            if self.current_label_resort is not None:
                labels = list(np.flip(np.array(labels)[self.current_label_resort]))
            labels = [(0.5 + i, l) for i, l in enumerate(labels)]
            self.plot.showAxis('right')
            ax = self.plot.getAxis('right')
            ax.setTickFont(QFont("Courier"))
            ax.setWidth(100)
            ax.setTicks([labels])

    def update_plot(self):
        key = self.content_cb.get_selected_key()
        module = self.content_cb.get_selected_module()
        if module is not None:
            image, self.current_label_resort = module.get_cluster_matrix(key)
            if image is not None:
                self.image_item.setImage(np.fliplr(image))



    def on_selected_neuron_changed(self, Network_UI):
        self.left_axis_cb.change_main_object(Network_UI.selected_neuron_group())
        self.content_cb.change_main_object(Network_UI.selected_neuron_group())
        self.right_axis_cb.change_main_object(Network_UI.selected_neuron_group())
        self.update_plot()

    def initialize(self, Network_UI):
        self.similarity_matrix_tab = Network_UI.Next_Tab(self.title)

        self.image_item, self.plot = Network_UI.Add_Image_Item(True, False, title='', tooltip_message='afferent synapse weights of selected neuron')

        cmap = generatePgColormap('viridis')

        self.image_item.setLookupTable(cmap.getLookupTable())

        Network_UI.Next_H_Block()

        self.current_label_resort = None

        self.left_axis_cb = Network_UI.Add_element(Analytics_Results_Select_ComboBox(Network_UI.network.NeuronGroups[0], 'labeler', first_entry=''))
        self.content_cb = Network_UI.Add_element(Analytics_Results_Select_ComboBox(Network_UI.network.NeuronGroups[0], 'cluster_matrix_classifier'))
        self.right_axis_cb = Network_UI.Add_element(Analytics_Results_Select_ComboBox(Network_UI.network.NeuronGroups[0], 'labeler', first_entry=''))


        def update_btn_clicked(event):
            self.update_plot()
            self.update_labels()

        self.update_btn = Network_UI.Add_element(QPushButton('update'))
        self.update_btn.clicked.connect(update_btn_clicked)


    def update(self, Network_UI):
        if self.similarity_matrix_tab.isVisible():
            self.current_group = Network_UI.selected_neuron_group()



