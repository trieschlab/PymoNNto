from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np


class inh_exc_tab():

    def add_recorder_variables(self, neuron_group, recorder):
        if hasattr(neuron_group, 'excitation'):
            recorder.add_varable('n.excitation')
        if hasattr(neuron_group, 'inhibition'):
            recorder.add_varable('n.inhibition')
        if hasattr(neuron_group, 'input_act'):
            recorder.add_varable('n.input_act')
        if hasattr(neuron_group, 'TH'):
            recorder.add_varable('n.TH')
            recorder.add_varable('np.mean(n.TH)')

    def initialize(self, Network_UI):
        self.inh_exc_tab = Network_UI.Next_Tab('inh exc')

        curves = Network_UI.Add_plot_curve('net exc vs inh', number_of_curves=5, lines=[0], names=['act', 'inh', 'exc', 'TH', 'inp'])

        self.net_exc_curve = curves[2]
        self.net_inh_curve = curves[1]
        self.net_exc_inh_curve = curves[0]
        self.net_inh_exc_TH_curve = curves[3]
        self.net_inp_curve = curves[4]

        Network_UI.Next_H_Block()

        curves = Network_UI.Add_plot_curve('neuron exc vs inh', number_of_curves=5, lines=[0], names=['act', 'inh', 'exc', 'TH', 'inp'])
        self.neuron_exc_curve = curves[2]
        self.neuron_inh_curve = curves[1]
        self.neuron_exc_inh_curve = curves[0]
        self.neuron_inh_exc_TH_curve = curves[3]
        self.neuron_inp_curve = curves[4]

        # self.train_btn = QPushButton('train', self.main_window)
        # self.train_btn.clicked.connect(train_click)
        # self.Add_element(self.train_btn)

        Network_UI.Next_H_Block()

        self.show_threshold_cb = QCheckBox()
        self.show_threshold_cb.setText('show threshold')
        self.show_threshold_cb.setChecked(True)
        Network_UI.Add_element(self.show_threshold_cb)


    def update(self, Network_UI):
        if self.inh_exc_tab.isVisible():
            group = Network_UI.network[Network_UI.neuron_select_group, 0]

            net_exc_inh_data = 0

            if hasattr(group, 'excitation'):
                net_exc_data = np.mean(group['n.excitation', 0, 'np'][-Network_UI.x_steps:], axis=1)
                net_exc_inh_data += net_exc_data
                self.net_exc_curve.setData(np.arange(Network_UI.it - len(net_exc_data), Network_UI.it), net_exc_data)

            if hasattr(group, 'inhibition'):
                net_inh_data = np.mean(group['n.inhibition', 0, 'np'][-Network_UI.x_steps:], axis=1)
                net_exc_inh_data += net_inh_data
                self.net_inh_curve.setData(np.arange(Network_UI.it - len(net_inh_data), Network_UI.it), net_inh_data)

            if hasattr(group, 'input_act'):
                net_inp_data = np.mean(group['n.input_act', 0, 'np'][-Network_UI.x_steps:], axis=1)
                net_exc_inh_data += net_inp_data
                self.net_inp_curve.setData(np.arange(Network_UI.it - len(net_inp_data), Network_UI.it), net_inp_data)

            if type(net_exc_inh_data) is not int:
                self.net_exc_inh_curve.setData(np.arange(Network_UI.it - len(net_exc_inh_data), Network_UI.it), net_exc_inh_data)

            if hasattr(group, 'TH'):
                net_TH_data = group['np.mean(n.TH)', 0, 'np'][-Network_UI.x_steps:].copy()
                if not self.show_threshold_cb.isChecked():
                    net_TH_data *= 0
                self.net_inh_exc_TH_curve.setData(np.arange(Network_UI.it - len(net_TH_data), Network_UI.it), net_TH_data)



            neuron_exc_inh_data = 0

            if hasattr(group, 'excitation'):
                neuron_exc_data = group['n.excitation', 0, 'np'][-Network_UI.x_steps:, Network_UI.neuron_select_id]
                neuron_exc_inh_data += neuron_exc_data
                self.neuron_exc_curve.setData(np.arange(Network_UI.it - len(neuron_exc_data), Network_UI.it), neuron_exc_data)

            if hasattr(group, 'inhibition'):
                neuron_inh_data = group['n.inhibition', 0, 'np'][-Network_UI.x_steps:, Network_UI.neuron_select_id]
                neuron_exc_inh_data += neuron_inh_data
                self.neuron_inh_curve.setData(np.arange(Network_UI.it - len(neuron_inh_data), Network_UI.it), neuron_inh_data)

            if hasattr(group, 'input_act'):
                neuron_inp_data = group['n.input_act', 0, 'np'][-Network_UI.x_steps:, Network_UI.neuron_select_id]
                neuron_exc_inh_data += neuron_inp_data
                self.neuron_inp_curve.setData(np.arange(Network_UI.it - len(neuron_inp_data), Network_UI.it), neuron_inp_data)

            if type(neuron_exc_inh_data) is not int:
                self.neuron_exc_inh_curve.setData(np.arange(Network_UI.it - len(neuron_exc_inh_data), Network_UI.it), neuron_exc_inh_data)

            if hasattr(group, 'TH'):
                neuron_TH_data = group['n.TH', 0, 'np'][-Network_UI.x_steps:, Network_UI.neuron_select_id].copy()
                if not self.show_threshold_cb.isChecked():
                    neuron_TH_data *= 0
                self.neuron_inh_exc_TH_curve.setData(np.arange(Network_UI.it - len(neuron_TH_data), Network_UI.it), neuron_TH_data)
