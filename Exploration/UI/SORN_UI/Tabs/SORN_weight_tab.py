from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np


class SORN_weight_tab():

    def add_recorder_variables(self, neuron_group, recorder):
        check = True
        for syn in neuron_group.afferent_synapses.get("All"):
            if not hasattr(syn, 'slow_add'):
                check = False
        if check:
            recorder.add_varable('[np.sum(s.slow_add) for s in n.afferent_synapses.get("All")]')

        check = True
        for syn in neuron_group.afferent_synapses.get("All"):
            if not hasattr(syn, 'fast_add'):
                check = False
        if check:
            recorder.add_varable('[np.sum(s.fast_add) for s in n.afferent_synapses.get("All")]')



    def initialize(self, SORN_UI):
        self.weight_tab = SORN_UI.Next_Tab('weights')

        #get max synapse group size
        max_sgs=2
        for group_tag in SORN_UI.group_tags:
            for ng in SORN_UI.network[group_tag]:
                for transmitter in SORN_UI.transmitters:
                    syns = SORN_UI.get_combined_syn_mats(ng[transmitter], None)
                    max_sgs = np.maximum(max_sgs, len(syns))

        self.transmitter_weight_images = {}
        for transmitter in SORN_UI.transmitters:
            self.transmitter_weight_images[transmitter] = []
            for _ in range(max_sgs):
                self.transmitter_weight_images[transmitter].append(SORN_UI.Add_Image_Item(True, False, title='Neuron '+transmitter+' W'))
            SORN_UI.Next_H_Block()

        _, self.input_plot_slow = SORN_UI.Add_plot_curve('Network average slow Inputs', return_plot=True, x_label='t (iterations)', y_label='Input')
        _, self.input_plot_fast = SORN_UI.Add_plot_curve('Network average fast Inputs', return_plot=True, x_label='t (iterations)', y_label='Input')




    def update(self, SORN_UI):
        if self.weight_tab.isVisible() and len(SORN_UI.network[SORN_UI.neuron_select_group]) > 0:

            group=SORN_UI.network[SORN_UI.neuron_select_group, 0]

            for transmitter in SORN_UI.transmitters:

                for image, plot in self.transmitter_weight_images[transmitter]:
                    plot.setTitle('')
                    image.clear()

                syns = SORN_UI.get_combined_syn_mats(group[transmitter], SORN_UI.neuron_select_id)
                for i, key in enumerate(syns):
                    self.transmitter_weight_images[transmitter][i][1].setTitle(key)
                    self.transmitter_weight_images[transmitter][i][0].setImage(np.rot90(syns[key], 3))


                #GABA_syns = SORN_UI.get_combined_syn_mats(SORN_UI.network[SORN_UI.neuron_select_group, 0]['GABA'], SORN_UI.neuron_select_id)
                #for i, key in enumerate(GABA_syns):
                #    self.weight_GABA_items[i][1].setTitle(key)
                #    self.weight_GABA_items[i][0].setImage(np.rot90(GABA_syns[key],3))



            self.input_plot_slow.clear()
            recorded = group['[np.sum(s.slow_add) for s in n.afferent_synapses.get("All")]']
            if len(recorded) > 0:
                inputs = np.array(recorded[0])
                ident=[s.src.group_without_subGroup() for s in group.afferent_synapses.get("All")]
                single_ident = list(set(ident))

                #if not hasattr(self, 'slow_input_colors'):
                #    self.slow_input_colors = [np.random.rand(3) * 255 for _ in single_ident]

                for i, si in enumerate(single_ident):
                    mask = [id == si for id in ident]

                    data = np.sum(inputs[-SORN_UI.x_steps:, mask], axis=1)
                    curve = pg.PlotCurveItem(np.arange(SORN_UI.it - len(data), SORN_UI.it), data, name='', pen=si.color)#self.slow_input_colors[i]
                    self.input_plot_slow.addItem(curve)



            self.input_plot_fast.clear()
            recorded = group['[np.sum(s.fast_add) for s in n.afferent_synapses.get("All")]']
            if len(recorded) > 0:
                inputs = np.array(recorded[0])
                ident = [s.src.group_without_subGroup() for s in group.afferent_synapses.get("All")]
                single_ident = list(set(ident))

                #if not hasattr(self, 'fast_input_colors'):
                #    self.fast_input_colors = [np.random.rand(3) * 255 for _ in single_ident]

                for i, si in enumerate(single_ident):
                    mask = [id == si for id in ident]

                    data = np.sum(inputs[-SORN_UI.x_steps:, mask], axis=1)
                    curve = pg.PlotCurveItem(np.arange(SORN_UI.it - len(data), SORN_UI.it), data, name='', pen=si.color)#self.fast_input_colors[i]
                    self.input_plot_fast.addItem(curve)





                # print(data.shape)
                # self.input_curves[i].setData(np.arange(it-len(data), it), data)

        #self.avg_big_synapses_data = []
        #self.neuron_big_synapses_data = []

        #self.weight_GLU_item, self.avg_big_synapses_curve = SORN_UI.Add_plot_curve('Number of big Synapses', number_of_curves=2, names=['neuron', 'average'])

        # self.avg_big_synapses_curve.setData(np.arange(it - len(self.avg_big_synapses_data), it), self.avg_big_synapses_data)
        # self.neuron_big_synapses_curve
        #self.weight_GLU_item = self.Add_Image_Item(False, False, title='Neuron GLU W')
        #self.weight_GABA_item = self.Add_Image_Item(False, False, title='Neuron GABA W')

        # limit data length to x_steps steps
        #if len(self.avg_big_synapses_data) > SORN_UI.x_steps: self.avg_big_synapses_data.pop(0)
        #if len(self.neuron_big_synapses_data) > SORN_UI.x_steps: self.neuron_big_synapses_data.pop(0)