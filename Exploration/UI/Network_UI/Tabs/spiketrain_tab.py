from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np


class spiketrain_tab():

    def add_recorder_variables(self, neuron_group, recorder):
        if hasattr(neuron_group, 'output'):
            recorder.add_varable('n.output')

    def initialize(self, Network_UI):
        self.scatter_tab = Network_UI.Next_Tab('spiketrain')

        self.spiketrain_images=[]
        for i, group_tag in enumerate(Network_UI.neuron_visible_groups):
            if i!=0:
                Network_UI.Next_H_Block()
            self.spiketrain_images.append(Network_UI.Add_Image_Item(False, tooltip_message='output of each neuron(rows) at each timestep(columns)'))


    def update(self, Network_UI):
        if self.scatter_tab.isVisible():
            for i, group_tag in enumerate(Network_UI.neuron_visible_groups):
                group = Network_UI.network[group_tag, 0]

                if hasattr(group, 'output'):
                    #image = np.dstack((np.reshape(r, shape), np.reshape(g, shape), np.reshape(b, shape)))
                    data = group['n.output', 0, 'np']
                    if group_tag == Network_UI.neuron_select_group:
                        id=Network_UI.neuron_select_id
                        data[:, id-1:id+2] += 0.2
                        data[:, id] += 0.3
                    self.spiketrain_images[i].setImage(data, levels=(0, 1))#np.rot90(, 3)