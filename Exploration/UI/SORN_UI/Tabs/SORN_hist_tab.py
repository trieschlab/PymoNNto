from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np

import matplotlib.pyplot as plt
from Exploration.Visualization.Visualization_Helper import *

#from X_Experimental.Functions import *


class SORN_hist_tab():

    def add_recorder_variables(self, neuron_group, recorder):
        if hasattr(neuron_group, 'output'):
            recorder.add_varable('n.output')#???

    def initialize(self, SORN_UI):
        self.additionaltab = SORN_UI.Next_Tab('hist')

        _, self.isi_plt = SORN_UI.Add_plot_curve('one neuron isi hist', True, False, legend=False, x_label='ISI', y_label='Frequency')
        _, self.net_avg_hist_plt = SORN_UI.Add_plot_curve('net avg activities (1000 steps)', True, False, legend=False, x_label='average activity', y_label='Frequency')
        _, self.input_avg_hist_plt = SORN_UI.Add_plot_curve('input avg activities (1000 steps)', True, False, legend=False, x_label='average activity', y_label='Frequency')

        self.weight_hist_plots = {}
        self.net_weight_hist_plots = {}
        self.net_inp_weight_hist_plots = {}

        for transmitter in SORN_UI.transmitters:
            SORN_UI.Next_H_Block()
            _, self.weight_hist_plots[transmitter] = SORN_UI.Add_plot_curve(transmitter + ' weight hist', True, False, legend=False, x_label=transmitter + ' synapse size', y_label='Frequency')
            _, self.net_weight_hist_plots[transmitter] = SORN_UI.Add_plot_curve(transmitter + ' network weight hist', True, False, legend=False, x_label=transmitter + ' synapse size', y_label='Frequency')
            _, self.net_inp_weight_hist_plots[transmitter] = SORN_UI.Add_plot_curve(transmitter + ' network input weight hist', True, False, legend=False, x_label=transmitter + ' synapse size', y_label='Frequency')

        #SORN_UI.Next_H_Block()
        #_, self.gaba_weight_hist_plt = SORN_UI.Add_plot_curve('GABA weight hist', True, False, legend=False)
        #_, self.gaba_net_weight_hist_plt = SORN_UI.Add_plot_curve('GABA network weight hist', True, False, legend=False)
        #_, self.gaba_net_inp_weight_hist_plt = SORN_UI.Add_plot_curve('GABA network input weight hist', True, False, legend=False)

        SORN_UI.Next_H_Block()
        self.min_hist_slider = QSlider(1)  # QtCore.Horizontal
        self.min_hist_slider.setMinimum(-1)
        self.min_hist_slider.setMaximum(10)
        self.min_hist_slider.setSliderPosition(-1)
        self.min_hist_slider.mouseReleaseEvent = SORN_UI.static_update_func
        SORN_UI.Add_element(self.min_hist_slider)  # , stretch=0.1

        # self.Next_H_Block()

        def wnwi_click(event):
            image = get_whole_Network_weight_image(SORN_UI.network[SORN_UI.exc_group_name, 0], neuron_src_groups=None, individual_norm=True, exc_weight_attr='W', inh_weight_attr='W', activations=SORN_UI.network[SORN_UI.exc_group_name, 0].output)
            plt.imshow(image, interpolation="nearest")
            plt.show()

        self.wnwi_btn = QPushButton('whole network weight image', SORN_UI.main_window)
        self.wnwi_btn.clicked.connect(wnwi_click)
        SORN_UI.Add_element(self.wnwi_btn)

        # self.Next_H_Block()

        # def ttp1_click(event):
        #    plot_t_vs_tp1(np.mean(np.array(self.network[self.neuron_select_group,0]['n.output', 0][-1000:]), axis=1))
        # self.ttp1_btn = QPushButton('net t vs t+1 plot (1k)', self.main_window)
        # self.ttp1_btn.clicked.connect(ttp1_click)
        # self.Add_element(self.ttp1_btn)

        # def ives_click(event):
        #    inh=np.array(self.network[self.neuron_select_group, 0]['n.inhibition', 0][-1000:])
        #    exc=np.array(self.network[self.neuron_select_group, 0]['n.excitation', 0][-1000:])
        #    inhibition_excitation_scatter(inh,exc)
        # self.ives_btn = QPushButton('net inhibition vs excitation scatter (1k)', self.main_window)
        # self.ives_btn.clicked.connect(ives_click)
        # self.Add_element(self.ives_btn)


    def update(self, SORN_UI):
        if self.additionaltab.isVisible():

            group = SORN_UI.network[SORN_UI.neuron_select_group, 0]

            if hasattr(group, 'Input_Mask'):
                input_mask = group.Input_Mask
                not_input_mask = np.invert(input_mask)
            else:
                input_mask = False
                not_input_mask = True

            msl = self.min_hist_slider.sliderPosition() * 0.001

            net_color_input = (group.color[0]*0.5, group.color[1]*0.5, group.color[2]*0.5, 255)

            if hasattr(group, 'output'):
                self.neuron_act_data = group['n.output', 0, 'np'][-5000:, SORN_UI.neuron_select_id]
                self.isi_plt.clear()
                y, x = np.histogram(SpikeTrain_ISI(self.neuron_act_data), bins=15)
                curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=(0, 255, 0, 255))
                self.isi_plt.addItem(curve)

                self.net_avg_hist_plt.clear()
                avg_acts = np.mean(group['n.output', 0, 'np'][-SORN_UI.x_steps:, not_input_mask], axis=0)#1000
                y, x = np.histogram(avg_acts, bins=25)
                curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=group.color)
                self.net_avg_hist_plt.addItem(curve)

                self.input_avg_hist_plt.clear()
                if input_mask is not False:
                    input_avg_acts = np.mean(group['n.output', 0, 'np'][-SORN_UI.x_steps:, input_mask], axis=0)#1000
                    y, x = np.histogram(input_avg_acts, bins=25)
                    curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=net_color_input)#todo:make faster!
                    self.input_avg_hist_plt.addItem(curve)#todo:make faster!


            for transmitter in SORN_UI.transmitters:

                glu_syns = group[transmitter]
                if len(glu_syns) > 0:
                    GLU_syn = SORN_UI.get_combined_syn_mats(glu_syns)

                    GLU_syn = GLU_syn[list(GLU_syn.keys())[0]]
                    selected_neuron_GLU_syn = GLU_syn[SORN_UI.neuron_select_id]
                    # print(GLU_syn.shape, selected_neuron_GLU_syn.shape)

                    # self.hist_plt.clear()
                    # y, x = np.histogram(np.sum(GLU_syn.transpose() > (np.max(GLU_syn, axis=1) * (1 / 2)), axis=0), bins=10)
                    # curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 255))
                    # self.hist_plt.addItem(curve)


                    if input_mask is not False:
                        self.net_inp_weight_hist_plots[transmitter].clear()
                        y, x = np.histogram(GLU_syn[input_mask][GLU_syn[input_mask] > msl], bins=50)
                        curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=net_color_input)
                        self.net_inp_weight_hist_plots[transmitter].addItem(curve)


                    self.net_weight_hist_plots[transmitter].clear()
                    y, x = np.histogram(GLU_syn[not_input_mask][GLU_syn[not_input_mask] > msl], bins=50)
                    curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=group.color)
                    self.net_weight_hist_plots[transmitter].addItem(curve)

                    self.weight_hist_plots[transmitter].clear()
                    y, x = np.histogram(selected_neuron_GLU_syn[selected_neuron_GLU_syn > msl], bins=50)
                    curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=(0, 255, 0, 255))
                    self.weight_hist_plots[transmitter].addItem(curve)
                else:
                    self.net_inp_weight_hist_plots[transmitter].clear()
                    self.net_weight_hist_plots[transmitter].clear()
                    self.weight_hist_plots[transmitter].clear()


            '''
            gaba_syns = nsg['GABA']
            if len(gaba_syns) > 0:
                GABA_syn = SORN_UI.get_combined_syn_mats(gaba_syns)
                GABA_syn = GABA_syn[list(GABA_syn.keys())[0]]
                selected_neuron_GABA_syn = GABA_syn[SORN_UI.neuron_select_id]
                # print(GABA_syn.shape, selected_neuron_GABA_syn.shape)

                self.gaba_net_inp_weight_hist_plt.clear()
                if hasattr(nsg, 'Input_Mask'):
                    input_mask = nsg.Input_Mask

                    y, x = np.histogram(GABA_syn[input_mask][GABA_syn[input_mask] > msl], bins=50)
                    curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 255))
                    self.gaba_net_inp_weight_hist_plt.addItem(curve)

                else:
                    input_mask = False

                self.gaba_net_weight_hist_plt.clear()
                y, x = np.histogram(GABA_syn[input_mask * -1][GABA_syn[input_mask * -1] > msl], bins=50)
                curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=net_color)
                self.gaba_net_weight_hist_plt.addItem(curve)

                self.gaba_weight_hist_plt.clear()
                y, x = np.histogram(selected_neuron_GABA_syn[selected_neuron_GABA_syn > msl], bins=50)
                curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=(0, 255, 0, 255))
                self.gaba_weight_hist_plt.addItem(curve)
            # else:
            #    clear...
            '''