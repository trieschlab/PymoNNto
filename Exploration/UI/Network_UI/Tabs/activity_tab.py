from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np


class activity_tab():

    def __init__(self, variables):
        self.variables = variables

    def add_recorder_variables(self, neuron_group, recorder):

        for var in self.variables:
            if hasattr(neuron_group, var):
                recorder.add_varable('n.'+var)
                recorder.add_varable('np.mean(n.'+var+')')

        '''
        if hasattr(neuron_group, 'output'):
            recorder.add_varable('n.output')#???
            recorder.add_varable('np.mean(n.output)')
        if hasattr(neuron_group, 'TH'):
            recorder.add_varable('n.TH')
            recorder.add_varable('np.mean(n.TH)')
        if hasattr(neuron_group, 'weight_norm_factor'):
            recorder.add_varable('n.weight_norm_factor')
            recorder.add_varable('np.mean(n.weight_norm_factor)')
        if hasattr(neuron_group, 'nox'):
            recorder.add_varable('n.nox')
            recorder.add_varable('np.average(n.nox)')
        if hasattr(neuron_group, 'refractory_counter'):
            recorder.add_varable('n.refractory_counter')
        '''



    def initialize(self, Network_UI):
        self.main_tab = Network_UI.Next_Tab('Activity')

        #self.sliders = []
        #lines = []



        #if len(Network_UI.network['IPTI'])>0:

        self.net_var_curves={}
        for i, var in enumerate(self.variables):
            stretch=1
            if i==0:
                stretch=2
            self.net_var_curves[var] = Network_UI.Add_plot_curve(stretch=stretch, number_of_curves=len(Network_UI.neuron_visible_groups), return_list=True, x_label='t (iterations)', y_label='Network average ' + var)

        #self.network['grammar_act', 0].mean_network_input_activity]#(900 / 60) / 900
        #self.avg_act_curves = Network_UI.Add_plot_curve(stretch=2, number_of_curves=len(Network_UI.neuron_visible_groups), lines=lines, return_list=True, x_label='t (iterations)', y_label='Network average activity')
        #self.avg_TH_curves = Network_UI.Add_plot_curve(number_of_curves=len(Network_UI.neuron_visible_groups), return_list=True, x_label='t (iterations)', y_label='Network average threshold')
        #self.net_avg_nox_curves = Network_UI.Add_plot_curve(number_of_curves=len(Network_UI.neuron_visible_groups), return_list=True, x_label='t (iterations)', y_label='Network average NOX')
        #self.avg_norm_weight_curves = Network_UI.Add_plot_curve(number_of_curves=len(Network_UI.neuron_visible_groups), return_list=True, x_label='t (iterations)', y_label='Network average norm factor')

        '''
        for group_tag in Network_UI.neuron_visible_groups:

            mechanisms=Network_UI.network[group_tag, 0]['IPTI']
            if len(mechanisms)>0 and hasattr(mechanisms[0], 'th'):
                lines.append(np.mean(mechanisms[0].th))
            #lines.append(np.mean(Network_UI.network['IPTI', 0].min_th))
            #lines.append(np.mean(Network_UI.network['IPTI', 0].max_th))

            v_layout = QVBoxLayout()
            self.sliders.append(QSlider(0))#QtCore.Horizontal
            self.sliders[-1].setMinimum(0)
            self.sliders[-1].setMaximum(100)
            self.sliders[-1].setSliderPosition(100)
            self.sliders[-1].mouseReleaseEvent = Network_UI.static_update_func
            v_layout.addWidget(self.sliders[-1], stretch=0.1)
            Network_UI.current_H_block.addLayout(v_layout)
            #Network_UI.Add_element(self.sliders[-1], stretch=0.1)
        '''

        Network_UI.Next_H_Block()

        self.neuron_var_curves = {}
        for i, var in enumerate(self.variables):
            stretch = 1
            if i == 0:
                stretch = 2
            self.neuron_var_curves[var] = Network_UI.Add_plot_curve(stretch=stretch, colors=[(0, 255, 0)], legend=False, x_label='t (iterations)', y_label='Neuron ' + var)

        #self.neuron_act_curve, self.refractory_counter_curve = Network_UI.Add_plot_curve(number_of_curves=2, stretch=2, colors=[(0, 255, 0), (180, 120, 0)], lines=[0.1], legend=False, x_label='t (iterations)', y_label='Neuron output')
        #self.neuron_th_curve = Network_UI.Add_plot_curve(colors=[(0, 255, 0)], legend=False, x_label='t (iterations)', y_label='Neuron threshold')
        #self.neuron_nox_curve = Network_UI.Add_plot_curve(colors=[(0, 255, 0)], legend=False, x_label='t (iterations)', y_label='Neuron NOX')
        #self.neuron_norm_weight = Network_UI.Add_plot_curve(colors=[(0, 255, 0)], legend=False, number_of_curves=1, x_label='t (iterations)', y_label='Neuron norm factor')


    def update(self, Network_UI):
        if self.main_tab.isVisible():


            for i, group_tag in enumerate(Network_UI.neuron_visible_groups):
                if len(Network_UI.network[group_tag]) > 0:
                    group=Network_UI.network[group_tag, 0]
                    squeeze= Network_UI.group_sliders[i].sliderPosition() / 100
                    #squeeze = self.sliders[i].sliderPosition() / 100

                    for var in self.variables:
                        if hasattr(group, var):
                            net_data = group['np.mean(n.'+var+')', 0, 'np'][-Network_UI.x_steps:]
                            self.net_var_curves[var][i].setData(np.arange(Network_UI.it - len(net_data), Network_UI.it), net_data * squeeze, pen=group.color)
                        else:
                            self.net_var_curves[var][i].clear()

                    '''
                    if hasattr(group, 'output'):
                        net_avg_data = group['np.mean(n.output)', 0, 'np'][-Network_UI.x_steps:]
                        self.avg_act_curves[i].setData(np.arange(Network_UI.it - len(net_avg_data), Network_UI.it), net_avg_data * squeeze, pen=group.color)
                    else:
                        self.avg_act_curves[i].clear()

                    if hasattr(group, 'TH'):
                        net_avg_th_data = group['np.mean(n.TH)', 0, 'np'][-Network_UI.x_steps:]
                        self.avg_TH_curves[i].setData(np.arange(Network_UI.it - len(net_avg_th_data), Network_UI.it),net_avg_th_data, pen=group.color)
                    else:
                        self.avg_TH_curves[i].clear()

                    if hasattr(group, 'nox'):
                        net_avg_nox = group['np.average(n.nox)', 0, 'np'][-Network_UI.x_steps:]
                        self.net_avg_nox_curves[i].setData(np.arange(Network_UI.it - len(net_avg_nox), Network_UI.it), net_avg_nox, pen=group.color)
                    else:
                        self.net_avg_nox_curves[i].clear()

                    if hasattr(group, 'weight_norm_factor'):
                        net_avg_norm_weight = group['np.mean(n.weight_norm_factor)', 0, 'np'][-Network_UI.x_steps:]
                        self.avg_norm_weight_curves[i].setData(np.arange(Network_UI.it - len(net_avg_norm_weight), Network_UI.it), net_avg_norm_weight, pen=group.color)
                    else:
                        self.net_avg_nox_curves[i].clear()
                    '''

            '''
            if len(Network_UI.network[Network_UI.exc_group_name]) > 0:
                net_avg_data = Network_UI.network[Network_UI.exc_group_name, 0]['np.mean(n.output)', 0, 'np'][-Network_UI.x_steps:]
                net_avg_th_data = Network_UI.network[Network_UI.exc_group_name, 0]['np.mean(n.TH)', 0, 'np'][-Network_UI.x_steps:]
                net_avg_norm_weight = Network_UI.network[Network_UI.exc_group_name, 0]['np.mean(n.weight_norm_factor)', 0, 'np'][-Network_UI.x_steps:]
                net_avg_nox = Network_UI.network[Network_UI.exc_group_name, 0]['np.average(n.nox)', 0, 'np'][-Network_UI.x_steps:]
                self.avg_norm_weight.setData(np.arange(Network_UI.it - len(net_avg_norm_weight), Network_UI.it),net_avg_norm_weight)
                self.net_avg_nox_curve.setData(np.arange(Network_UI.it - len(net_avg_nox), Network_UI.it), net_avg_nox)
                self.net_avg_curve.setData(np.arange(Network_UI.it - len(net_avg_data), Network_UI.it), net_avg_data)
                self.net_avg_th_curve.setData(np.arange(Network_UI.it - len(net_avg_th_data), Network_UI.it), net_avg_th_data)

            if len(Network_UI.network[Network_UI.inh_group_name]) > 0:
                net_avg_inh_data = Network_UI.network[Network_UI.inh_group_name, 0]['np.mean(n.output)', 0, 'np'][-Network_UI.x_steps:]
                net_avg_inh_th_data = Network_UI.network[Network_UI.inh_group_name, 0]['np.mean(n.TH)', 0, 'np'][-Network_UI.x_steps:]
                self.net_avg_inh_curve.setData(np.arange(Network_UI.it - len(net_avg_inh_data), Network_UI.it), np.array(net_avg_inh_data) * squeeze)
                self.net_avg_inh_th_curve.setData(np.arange(Network_UI.it - len(net_avg_inh_th_data), Network_UI.it), net_avg_inh_th_data)
            '''

            group = Network_UI.network[Network_UI.neuron_select_group, 0]

            for var in self.variables:
                if hasattr(group, var):
                    neuron_data = group['n.' + var, 0, 'np']
                    if len(neuron_data.shape) > 1:
                        neuron_data = neuron_data[-Network_UI.x_steps:, Network_UI.neuron_select_id]
                    else:
                        neuron_data = neuron_data[-Network_UI.x_steps:]
                    self.neuron_var_curves[var].setData(np.arange(Network_UI.it - len(neuron_data), Network_UI.it), neuron_data)
                else:
                    self.neuron_var_curves[var].clear()

            '''
            if hasattr(group, 'output'):
                neuron_act_data = group['n.output', 0, 'np'][-Network_UI.x_steps:, Network_UI.neuron_select_id]
                self.neuron_act_curve.setData(np.arange(Network_UI.it - len(neuron_act_data), Network_UI.it), neuron_act_data)
            else:
                self.neuron_act_curve.clear()

            if hasattr(group, 'TH') and type(group.TH) is np.ndarray:
                neuron_th_data = group['n.TH', 0, 'np'][-Network_UI.x_steps:, Network_UI.neuron_select_id]
                self.neuron_th_curve.setData(np.arange(Network_UI.it - len(neuron_th_data), Network_UI.it), neuron_th_data)
            else:
                self.neuron_th_curve.clear()

            if hasattr(group, 'refractory_counter'):
                refractory_counter_data = group['n.refractory_counter', 0, 'np'][-Network_UI.x_steps:, Network_UI.neuron_select_id]
                self.refractory_counter_curve.setData(np.arange(Network_UI.it - len(refractory_counter_data), Network_UI.it), refractory_counter_data)
            else:
                self.refractory_counter_curve.clear()

            if hasattr(group, 'weight_norm_factor'):
                neuron_norm_weight = group['n.weight_norm_factor', 0, 'np'][-Network_UI.x_steps:, Network_UI.neuron_select_id]
                self.neuron_norm_weight.setData(np.arange(Network_UI.it - len(neuron_norm_weight), Network_UI.it), neuron_norm_weight)
            else:
                self.neuron_norm_weight.clear()

            if hasattr(group, 'nox'):
                neuron_nox = group['n.nox', 0, 'np'][-Network_UI.x_steps:, Network_UI.neuron_select_id]
                self.neuron_nox_curve.setData(np.arange(Network_UI.it - len(neuron_th_data), Network_UI.it), neuron_nox)
            else:
                self.neuron_nox_curve.clear()
            '''

        #self.net_avg_plt.setLimits(xMin=None, xMax=None, yMin=-0.01, yMax=0.5)
        #self.net_avg_plt.setRange(rect=None, xRange=None, yRange=[0,0.1], padding=None, update=True, disableAutoRange=True)
        #self.net_avg_plt.setYRange(min=0, max=None, padding=None, update=True)