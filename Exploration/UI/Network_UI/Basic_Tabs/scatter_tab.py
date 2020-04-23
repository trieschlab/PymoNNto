from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np


class scatter_tab():

    def __init__(self, x_var, y_var, title='Scatter', timesteps=500):
        self.x_var = x_var
        self.y_var = y_var
        self.title = title
        self.timesteps=timesteps

    def add_recorder_variables(self, neuron_group, Network_UI):
        if hasattr(neuron_group, self.x_var):
            Network_UI.add_recording_variable(neuron_group, 'n.' + self.x_var, timesteps=self.timesteps)
        if hasattr(neuron_group, self.y_var):
            Network_UI.add_recording_variable(neuron_group, 'n.' + self.y_var, timesteps=self.timesteps)

    def initialize(self, Network_UI):
        self.scatter_tab = Network_UI.Next_Tab(self.title)

        p = Network_UI.Add_plot(x_label=self.x_var, y_label=self.y_var)
        self.scatter_items=[]
        for i, _ in enumerate(Network_UI.neuron_visible_groups):
            spi = pg.ScatterPlotItem()
            self.scatter_items.append(spi)
            p.addItem(spi)
            #Network_UI.Next_H_Block()

    def update(self, Network_UI):
        if self.scatter_tab.isVisible():
            for i, group_tag in enumerate(Network_UI.neuron_visible_groups):
                if len(Network_UI.network[group_tag]) > 0:
                    group = Network_UI.network[group_tag, 0]
                    #group=Network_UI.network[Network_UI.neuron_select_group, 0]

                    if hasattr(group, self.x_var) and hasattr(group, self.y_var):
                        #rec = Network_UI.rec(group, self.timesteps)
                        x_values = group['n.'+self.x_var, 0, 'np'][-self.timesteps:]
                        y_values = group['n.'+self.y_var, 0, 'np'][-self.timesteps:]

                        x_val = np.mean(x_values, axis=0)
                        y_val = np.mean(y_values, axis=0)

                        self.scatter_items[i].setData(x_val.copy(), y_val.copy(), brush=group.color)
