from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np

from PyQt5.QtCore import QDate, Qt

from Exploration.Visualization.Reconstruct_Analyze_Label.Reconstruct_Analyze_Label import *

class character_activation_tab():

    def __init__(self, title='char'):
        self.title = title

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def initialize(self, Network_UI):
        if Network_UI.network['grammar_act', 0] is not None:
            self.reconstruction_tab = Network_UI.Next_Tab(self.title)


            source=Network_UI.network['grammar_act', 0]

            self.char_Act_plots = Network_UI.Add_plot_curve(number_of_curves=len(source.alphabet), x_label='t (iterations)', y_label='Network average ')

            for plot in self.char_Act_plots:
                plot.data=[]

            #self.data = np.zeros((len(source.alphabet),1))

            #self.timesteps=100


    def update(self, Network_UI):
        if Network_UI.network['grammar_act', 0] is not None and self.reconstruction_tab.isVisible():
            group=Network_UI.network[Network_UI.neuron_select_group, 0]
            #iterations = group['n.iteration', 0, 'np'][-self.timesteps:]

            if hasattr(group, 'Input_Weights') and hasattr(group, 'output'):
                activation = group.Input_Weights.transpose().dot(group.output)

                for i, plot in enumerate(self.char_Act_plots):
                    plot.data.append(activation[i])
                    plot.setData(plot.data)

                    if len(plot.data)>100:
                        plot.data=plot.data[1:]

                #if len(neuron_data.shape) > 1:
                #    neuron_data = neuron_data[:, Network_UI.neuron_select_id]
                #self.neuron_var_curves[var].setData(iterations, neuron_data)

                #self.char_Act_plots.setData(self.data)