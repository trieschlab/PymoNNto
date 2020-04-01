from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np

from Exploration.Visualization.Reconstruct_Analyze_Label.Reconstruct_Analyze_Label import *

class SORN_buffer_tab():

    def add_recorder_variables(self, neuron_group, recorder):
        return

    def initialize(self, SORN_UI):
        if SORN_UI.network['grammar_act', 0] is not None:
            self.buffertab = SORN_UI.Next_Tab('Buffer')

            alphabet = SORN_UI.network['grammar_act'][0].alphabet
            a_list = [alphabet[i] for i in range(len(alphabet))]
            a_list[0] = '_'
            ydict = dict(enumerate(a_list))

            win = pg.GraphicsWindow()
            stringaxis = pg.AxisItem(orientation='left')
            stringaxis.setTicks([ydict.items()])

            p = SORN_UI.Add_plot(axisItems={'left': stringaxis}, x_label='buffer steps')

            self.graph = pg.GraphItem()
            # p=self.Add_plot('', True)
            p.addItem(self.graph)

            source = SORN_UI.network['grammar_act'][0]
            RALN = Reconstruct_Analyze_Label_Network(SORN_UI.network)
            groups = SORN_UI.network['prediction_source']#SORN_UI.exc_group_name  # , network.NeuronGroups[1]

            def update():
                RALN.label_and_group_neurons(SORN_UI.network['prediction_source', 0], [source.get_activation(char, SORN_UI.network['prediction_source', 0]) for char in range(source.get_alphabet_length())], 'W', 20)
                _, self.edges = RALN.visualize_label_and_group_neurons(x_attribute_name='temporal_layer',
                                                                       y_attribute_name='class_label',
                                                                       weight_attribute_name='W',
                                                                       groups=groups,
                                                                       weight_limit=None,
                                                                       n_biggest=1,
                                                                       source=source,
                                                                       return_graph=True)  # 1/3#None#1/3#0.5

                self.nodes = RALN.get_neuron_positions(SORN_UI.network['prediction_source', 0],
                                                       x_attribute_name='temporal_layer',
                                                       y_attribute_name='class_label',
                                                       y_scale=0.0005)

            self.update_btn = QPushButton('update live buffers', SORN_UI.main_window)
            self.update_btn.clicked.connect(update)

            SORN_UI.Next_H_Block()
            SORN_UI.Add_element(self.update_btn)


            #def plot_buffer_chains(event):
            #    # self.network.NeuronGroups = [self.network.NeuronGroups[0]]
            #    # self.network.SynapseGroups = [self.network.SynapseGroups[0]]
            #    source = SORN_UI.network['grammar_act', 0]
            #    RALN = Reconstruct_Analyze_Label_Network(SORN_UI.network)
            #    groups = SORN_UI.network[SORN_UI.exc_group_name, 0]  # , network.NeuronGroups[1]
            #    RALN.label_and_group_neurons(SORN_UI.network[SORN_UI.exc_group_name, 0],
            #                                 [source.get_activation(char) for char in range(source.get_alphabet_length())],
            #                                 'W', 10)
            #    RALN.visualize_label_and_group_neurons(x_attribute_name='temporal_layer', y_attribute_name='class_label',
            #                                           weight_attribute_name='W', groups=groups, weight_limit=None,
            #                                           n_biggest=3, source=source)  # 1/3#None#1/3#0.5
            #
            #self.pbc_btn = QPushButton('plot buffer chains', SORN_UI.main_window)
            #self.pbc_btn.clicked.connect(plot_buffer_chains)
            #SORN_UI.Add_element(self.pbc_btn)
            # self.Add_Sidebar_Element(self.update_btn)


    def update(self, SORN_UI):
        if SORN_UI.network['grammar_act', 0] is not None and self.buffertab.isVisible() and hasattr(self, "nodes"):
            group = SORN_UI.network['prediction_source', 0]

            pos = np.array(self.nodes, dtype=float)
            colors = [(act * 255, 0, 0, 50) for act in group.output]

            if SORN_UI.network[SORN_UI.neuron_select_group, 0] is SORN_UI.network['prediction_source', 0]:
                GLU_syn = SORN_UI.get_combined_syn_mats(group['GLU'])
                GLU_syn = GLU_syn[list(GLU_syn.keys())[0]]
                big_syn_indices = np.where(GLU_syn[SORN_UI.neuron_select_id] > (np.max(GLU_syn[SORN_UI.neuron_select_id]) * (1 / 2)))[0]
                adj = np.array([[s, SORN_UI.neuron_select_id] for s in big_syn_indices])  # np.array(self.edges)##[self.neuron_select_id, 1]
                colors[SORN_UI.neuron_select_id] = (0, 255, 0, 255)
                self.graph.setData(pos=pos, adj=adj, size=0.5, symbol='o', pxMode=False, symbolBrush=colors, symbolPen=None)
            else:
                self.graph.setData(pos=pos, size=0.5, symbol='o', pxMode=False, symbolBrush=colors, symbolPen=None)

            self.graph.update()

            #selected_GLU_syn = GLU_syn[SORN_UI.neuron_select_id]

            #GABA_syn = SORN_UI.network[SORN_UI.neuron_select_group, 0]['GABA']
            #if len(GABA_syn) > 0:
            #    GABA_syn = SORN_UI.get_combined_syn_mats(GABA_syn)
            #    GABA_syn = GABA_syn[list(GABA_syn.keys())[0]]
            #    selected_GABA_syn = GABA_syn[SORN_UI.neuron_select_id]
            #else:
            #    GABA_syn = None
