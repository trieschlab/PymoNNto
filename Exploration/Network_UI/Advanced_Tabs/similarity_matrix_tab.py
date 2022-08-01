from PymoNNto.Exploration.Network_UI.Network_UI import *
from PymoNNto.Exploration.Network_UI.TabBase import *
import scipy.cluster.hierarchy as sch
import pandas as pd
import matplotlib.pyplot as plt

def generatePgColormap(cm_name):
    pltMap = plt.get_cmap(cm_name)
    colors = pltMap.colors
    colors = [c + [1.] for c in colors]
    positions = np.linspace(0, 1, len(colors))
    #print(positions, colors)
    pgMap = pg.ColorMap(positions, np.array(colors)*255.0)
    return pgMap


'''
def cluster_corr(corr_array, inplace=False):
    pairwise_distances = sch.distance.pdist(corr_array)
    linkage = sch.linkage(pairwise_distances, method='complete')
    cluster_distance_threshold = pairwise_distances.max() / 2
    idx_to_cluster_array = sch.fcluster(linkage, cluster_distance_threshold, criterion='distance')
    idx = np.argsort(idx_to_cluster_array)

    if not inplace:
        corr_array = corr_array.copy()

    if isinstance(corr_array, pd.DataFrame):
        return corr_array.iloc[idx, :].T.iloc[idx, :], idx

    return corr_array[idx, :][:, idx], idx
'''

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


        #key = self.left_axis_cb.get_selected_key()
        #module = self.left_axis_cb.get_selected_module()
        #if module is not None:


        #for
        #r = self.current_group['Neuron_Reaction_Analysis', 0]
        #if r is not None:
        #    labels = r.get_representations()

        #    if self.current_label_resort is not None:
        #        labels = list(np.array(labels)[self.current_label_resort])



    def update_plot(self):
        key = self.content_cb.get_selected_key()
        module = self.content_cb.get_selected_module()
        if module is not None:
            image, self.current_label_resort = module.get_cluster_matrix(key)
            if image is not None:
                self.image_item.setImage(np.fliplr(image))#np.fliplr(image)
            #else:
            #    print('image is none')
        #else:
        #    print('module is none')


    def on_selected_neuron_changed(self, Network_UI):
        self.left_axis_cb.change_main_object(Network_UI.selected_neuron_group())
        self.content_cb.change_main_object(Network_UI.selected_neuron_group())
        self.right_axis_cb.change_main_object(Network_UI.selected_neuron_group())
        self.update_plot()

    def initialize(self, Network_UI):
        self.similarity_matrix_tab = Network_UI.Next_Tab(self.title)

        self.image_item, self.plot = Network_UI.Add_Image_Item(True, False, title='', tooltip_message='afferent synapse weights of selected neuron')

        #colors = [
        #    (0, 0, 0),
        #    (4, 5, 61),
        #    (84, 42, 55),
        #    (15, 87, 60),
        #    (208, 17, 141),
        #    (255, 255, 255)
        #]
        # color map
        #cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 6), color=colors)
        #cmap = pg.get_cmap('CET-L9')
        cmap = generatePgColormap('viridis')

        self.image_item.setLookupTable(cmap.getLookupTable())
        #self.plot.setColorMap(cmap)

        #img = pg.ImageItem(image=noisy_data)  # create monochrome image from demonstration data
        #plot.addItem(img)  # add to PlotItem 'plot'
        #cm = pg.colormap.get('CET-L9')  # prepare a linear color map
        #bar = pg.ColorBarItem(values=(0, 20_000), cmap=cmap)  # prepare interactive color bar
        # Have ColorBarItem control colors of img and appear in 'plot':
        #bar.setImageItem(self.image_item, insert_in=self.plot)

        Network_UI.Next_H_Block()

        self.current_label_resort = None

        #self.similarity_images = {}
        #self.similarity_idxs = {}

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



