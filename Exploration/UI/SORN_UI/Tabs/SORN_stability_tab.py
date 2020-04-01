from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np

from Exploration.Visualization.Analysis_Plots import *

class SORN_stability_tab():

    def add_recorder_variables(self, neuron_group, recorder):
        if hasattr(neuron_group, 'output'):
            recorder.add_varable('n.output') # ???

    def initialize(self, SORN_UI):
        self.stab_tab = SORN_UI.Next_Tab('stability')

        self.image_items = []

        for group_tag1 in SORN_UI.neuron_visible_groups:
            self.image_items.append([])
            for group_tag2 in SORN_UI.neuron_visible_groups:
                self.image_items[-1].append(SORN_UI.Add_Image_Item(False, False, title=group_tag1+'(t) vs '+group_tag2+'(t+1)'))
            SORN_UI.Next_H_Block()



    def update(self, SORN_UI):
        if self.stab_tab.isVisible():

            for y, group_tag1 in enumerate(SORN_UI.neuron_visible_groups):
                for x, group_tag2 in enumerate(SORN_UI.neuron_visible_groups):

                    if len(SORN_UI.network[group_tag1]) >= 0 and len(SORN_UI.network[group_tag2]) >= 0:
                        group1 = SORN_UI.network[group_tag1, 0]
                        group2 = SORN_UI.network[group_tag2, 0]

                        if hasattr(group1, 'output') and hasattr(group2, 'output'):
                            act1 = np.mean(np.array(group1['n.output', 0][-1000:]), axis=1)
                            act2 = np.mean(np.array(group2['n.output', 0][-1000:]), axis=1)
                            self.image_items[y][x].setImage(get_t_vs_tp1_mat(act1, act2, 50, False))
