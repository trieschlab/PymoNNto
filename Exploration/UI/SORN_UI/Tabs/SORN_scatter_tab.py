from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np


class SORN_scatter_tab():

    def add_recorder_variables(self, neuron_group, recorder):
        if hasattr(neuron_group, 'excitation'):
            recorder.add_varable('n.excitation')
        if hasattr(neuron_group, 'inhibition'):
            recorder.add_varable('n.inhibition')

    def initialize(self, SORN_UI):
        self.scatter_tab = SORN_UI.Next_Tab('scatter')

        p = SORN_UI.Add_plot(x_label='Excitation', y_label='Inhibition')
        self.scatter = pg.ScatterPlotItem()
        p.addItem(self.scatter)

    def update(self, SORN_UI):
        if self.scatter_tab.isVisible():
            group=SORN_UI.network[SORN_UI.neuron_select_group, 0]

            if hasattr(group, 'excitation') and hasattr(group, 'inhibition'):
                exc = np.array(group['n.excitation', 0][-1000:])
                inh = np.array(group['n.inhibition', 0][-1000:])

                exc = np.mean(exc, axis=0)
                inh = np.mean(inh, axis=0)

                self.scatter.setData(exc, inh)
