from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np


class spiketrain_tab():

    def add_recorder_variables(self, neuron_group, recorder):
        if hasattr(neuron_group, 'output'):
            recorder.add_varable('n.output')

    def initialize(self, SORN_UI):
        self.scatter_tab = SORN_UI.Next_Tab('spiketrain')

        self.spiketrain_images=[]
        for i, group_tag in enumerate(SORN_UI.neuron_visible_groups):
            if i!=0:
                SORN_UI.Next_H_Block()
            self.spiketrain_images.append(SORN_UI.Add_Image_Item(False))


    def update(self, SORN_UI):
        if self.scatter_tab.isVisible():
            for i, group_tag in enumerate(SORN_UI.neuron_visible_groups):
                group = SORN_UI.network[group_tag, 0]

                if hasattr(group, 'output'):
                    #image = np.dstack((np.reshape(r, shape), np.reshape(g, shape), np.reshape(b, shape)))
                    data = group['n.output', 0, 'np']
                    if group_tag == SORN_UI.neuron_select_group:
                        id=SORN_UI.neuron_select_id
                        data[:, id-1:id+2] += 0.2
                        data[:, id] += 0.3
                    self.spiketrain_images[i].setImage(data, levels=(0, 1))#np.rot90(, 3)