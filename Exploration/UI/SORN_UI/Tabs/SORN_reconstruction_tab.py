from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np

from PyQt5.QtCore import QDate, Qt

from Exploration.Visualization.Reconstruct_Analyze_Label.Reconstruct_Analyze_Label import *

class SORN_reconstruction_tab():

    def add_recorder_variables(self, neuron_group, recorder):
        return

    def initialize(self, SORN_UI):
        if SORN_UI.network['grammar_act', 0] is not None:
            self.reconstruction_tab = SORN_UI.Next_Tab('recon')

            self.grid = QGridLayout()
            self.grid.setAlignment(Qt.AlignLeft)
            SORN_UI.current_H_block.addLayout(self.grid)
            SORN_UI.current_H_block.setAlignment(Qt.AlignTop)

            source = SORN_UI.network['grammar_act', 0]
            self.labels = []

            for y, char in enumerate(source.alphabet):
                self.labels.append([])
                for timestep in range(11):
                    label = QLabel('<font color='+('#%02x%02x%02x'% (timestep*25,timestep*25,timestep*25)).upper()+'>'+char.replace(' ','_')+'</font>')
                    label.char=char
                    self.labels[-1].append(label)
                    #label.setFont(QFont())
                    self.grid.addWidget(label, y, timestep)

            self.img = SORN_UI.Add_Image_Item(False, False, title=' neuron rec')

            self.recon_text_label = QLabel()
            SORN_UI.Add_element(self.recon_text_label)

            #SORN_UI.Next_H_Block()

            self.net_grid = QGridLayout()
            self.net_grid.setAlignment(Qt.AlignLeft)
            SORN_UI.current_H_block.addLayout(self.net_grid)
            SORN_UI.current_H_block.setAlignment(Qt.AlignTop)

            self.net_labels = []

            for y, char in enumerate(source.alphabet):
                self.net_labels.append([])
                for timestep in range(11):
                    net_label = QLabel('<font color='+('#%02x%02x%02x'% (timestep*25,timestep*25,timestep*25)).upper()+'>'+char.replace(' ','_')+'</font>')
                    net_label.char = char
                    self.net_labels[-1].append(net_label)
                    #label.setFont(QFont())
                    self.net_grid.addWidget(net_label, y, timestep)

            self.net_img = SORN_UI.Add_Image_Item(False, False, title='net rec')

            self.net_recon_text_label = QLabel()
            SORN_UI.Add_element(self.net_recon_text_label)






    def update(self, SORN_UI):
        if SORN_UI.network['grammar_act', 0] is not None and self.reconstruction_tab.isVisible():
            group=SORN_UI.network[SORN_UI.neuron_select_group, 0]

            RALN = Reconstruct_Analyze_Label_Network(SORN_UI.network)
            RALN.zero_recon()
            group.recon[SORN_UI.neuron_select_id] = 1
            RALN.propagation('W', 10, 'backward', 'forget', 'all', temporal_recon_groups=SORN_UI.network['prediction_source'], exponent=4, normalize=True, filter_weakest_percent=40.0)  # forget

            source = SORN_UI.network['grammar_act', 0]

            for ng in SORN_UI.network['prediction_source']:
                baseline = ng.Input_Weights.transpose().dot(ng.temporal_recon[-1])
                baseline = baseline/np.sum(baseline)

                if ng == group:#clicked group?
                    temp = ng.get_neuron_vec()
                    temp[SORN_UI.neuron_select_id] = 1.0
                    ng.temporal_recon.insert(0, temp)
                else:
                    ng.temporal_recon.append(ng.get_neuron_vec())

                text = ''
                res = []

                for r in ng.temporal_recon:
                    char_vec = ng.Input_Weights.transpose().dot(r)
                    s = np.sum(char_vec)
                    if s > 0:
                        char_vec = char_vec/s
                        res.insert(0, char_vec-baseline)
                        text = source.index_to_char(np.argmax(char_vec)) + text
                    else:
                        res.insert(0, np.zeros(ng.Input_Weights.shape[1]))
                        text = '#' + text

                text = list(text)
                start = text[0]
                for i, c in enumerate(text):
                    if text[i] == start:
                        text[i] = '#'
                    else:
                        break
                text = ''.join(text)

                res = np.array(res)
                res = res-np.min(res)
                self.img.setImage(np.fliplr(res.copy()))
                #res = np.array(res*res)

                for y in range(res.shape[0]):
                    for x in range(res.shape[1]):
                        m = (np.max(res)+np.max(res[y, :]))/2.0
                        if m == 0:
                            m = 1.0
                        val = 255-np.clip(int((res[y, x]-(np.mean(res[y, :])/2.0))/m*255.0), 0, None)
                        self.labels[x][y].setText('<font color='+('#%02x%02x%02x' % (val, val, val)).upper()+'>'+self.labels[x][y].char.replace(' ','_')+'</font>')

                self.recon_text_label.setText(text)

        ################################################################################################################
        ################################################################################################################
        ################################################################################################################

            RALN = Reconstruct_Analyze_Label_Network(SORN_UI.network)
            RALN.zero_recon()
            for ng in SORN_UI.network.NeuronGroups:
                ng.recon = ng.output_new.copy()
            RALN.propagation('W', 10, 'backward', 'forget', 'all', temporal_recon_groups=SORN_UI.network['prediction_source'], exponent=4, normalize=True, filter_weakest_percent=40.0)  # forget

            source = SORN_UI.network['grammar_act', 0]

            for ng in SORN_UI.network['prediction_source']:
                baseline = ng.Input_Weights.transpose().dot(ng.temporal_recon[-1])
                baseline = baseline / np.sum(baseline)

                ng.temporal_recon.append(ng.get_neuron_vec())

                text = ''
                res = []

                for r in ng.temporal_recon:
                    char_vec = ng.Input_Weights.transpose().dot(r)
                    s = np.sum(char_vec)
                    if s > 0:
                        char_vec = char_vec / s
                        res.insert(0, char_vec - baseline)
                        text = source.index_to_char(np.argmax(char_vec)) + text
                    else:
                        res.insert(0, np.zeros(ng.Input_Weights.shape[1]))
                        text = '#' + text

                text = list(text)
                start = text[0]
                for i, c in enumerate(text):
                    if text[i] == start:
                        text[i] = '#'
                    else:
                        break
                text = ''.join(text)

                res = np.array(res)
                res = res - np.min(res)
                self.net_img.setImage(np.fliplr(res.copy()))
                # res = np.array(res*res)

                for y in range(res.shape[0]):
                    for x in range(res.shape[1]):
                        m = (np.max(res) + np.max(res[y, :])) / 2.0
                        if m == 0:
                            m = 1.0

                        print()

                        val = 255 - np.clip(int((res[y, x] - (np.mean(res[y, :]) / 2.0)) / m * 255.0), 0, None)
                        self.net_labels[x][y].setText('<font color=' + ('#%02x%02x%02x' % (val, val, val)).upper() + '>' + self.net_labels[x][y].char.replace(' ','_') + '</font>')

                self.net_recon_text_label.setText(text)
