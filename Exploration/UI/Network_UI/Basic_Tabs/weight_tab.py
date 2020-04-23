from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np


class weight_tab():

    def __init__(self, title='Weights', weight_attr='W'):
        self.weight_attr = weight_attr
        self.title = title

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def initialize(self, Network_UI):
        self.weight_tab = Network_UI.Next_Tab(self.title)

        #get max synapse group size
        max_sgs=2
        for group_tag in Network_UI.group_tags:
            for ng in Network_UI.network[group_tag]:
                for transmitter in Network_UI.transmitters:
                    syns = Network_UI.get_combined_syn_mats(ng[transmitter], None, self.weight_attr)
                    max_sgs = np.maximum(max_sgs, len(syns))

        self.transmitter_weight_images = {}
        for transmitter in Network_UI.transmitters:
            self.transmitter_weight_images[transmitter] = []
            for _ in range(max_sgs):
                self.transmitter_weight_images[transmitter].append(Network_UI.Add_Image_Item(True, False, title='Neuron ' + transmitter + ' '+self.weight_attr, tooltip_message='afferent synapse weights of selected neuron'))
            Network_UI.Next_H_Block()

    def update(self, Network_UI):
        if self.weight_tab.isVisible() and len(Network_UI.network[Network_UI.neuron_select_group]) > 0:

            group = Network_UI.network[Network_UI.neuron_select_group, 0]

            for transmitter in Network_UI.transmitters:

                for image, plot in self.transmitter_weight_images[transmitter]:
                    plot.setTitle('')
                    image.clear()

                syns = Network_UI.get_combined_syn_mats(group[transmitter], Network_UI.neuron_select_id, self.weight_attr)
                for i, key in enumerate(syns):
                    self.transmitter_weight_images[transmitter][i][1].setTitle(key)
                    self.transmitter_weight_images[transmitter][i][0].setImage(np.rot90(syns[key], 3))