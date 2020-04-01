from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg

#from Testing.SORN.SORN_Helper import *

class SORN_UI_sidebar_grammar_module():

    def add_recorder_variables(self, neuron_group, recorder):
        if hasattr(neuron_group, 'output'):
            recorder.add_varable('n.output')

    def initialize(self, SORN_UI):
        if SORN_UI.network['grammar_act', 0] is not None:

            self.readout = None
            self.readout_simu = None

            # self.Add_Sidebar_Spacing()

            def learning_on_off(event):
                SORN_UI.network.set_mechanisms(['STDP'], self.stdp_cb.isChecked())

            self.stdp_cb = QCheckBox()
            self.stdp_cb.setText('STDP')
            self.stdp_cb.setChecked(True)
            self.stdp_cb.stateChanged.connect(learning_on_off)
            SORN_UI.Add_Sidebar_Element(self.stdp_cb)

            def grammar_activator_on_off(event):
                SORN_UI.network['grammar_act', 0].active = self.input_select_box.currentText() != 'None'

            self.input_select_box = QComboBox()
            self.input_select_box.addItem("Grammar Act.")
            self.input_select_box.addItem("Prediction")
            self.input_select_box.addItem("None")
            self.input_select_box.currentIndexChanged.connect(grammar_activator_on_off)
            SORN_UI.Add_Sidebar_Element(self.input_select_box)

            self.inp_text_label = QLabel(SORN_UI.main_window)
            SORN_UI.Add_Sidebar_Element(self.inp_text_label, stretch=0.2)
            self.inp_text_label.setText('')
            self.text = []

            def train_click(event):

                #SORN_UI.network.recording_off()

                SORN_UI.network.add_behaviours_to_neuron_groups({100: NeuronRecorder(['n.output'], tag='pediction_rec')}, SORN_UI.network['prediction_source'])
                SORN_UI.network.add_behaviours_to_neuron_groups({101: NeuronRecorder(['n.pattern_index'], tag='index_rec')}, SORN_UI.network['text_input_group'])

                #for ng in SORN_UI.network['prediction_source']:
                #    SORN_UI.network.add_behaviours_to_neuron_group({100: NeuronRecorder(['n.output'], tag='pediction_rec')}, ng)
                #for ng in SORN_UI.network['text_input_group']:
                #    SORN_UI.network.add_behaviours_to_neuron_group({101: NeuronRecorder(['n.pattern_index'], tag='index_rec')}, ng)


                SORN_UI.network['grammar_act', 0].active = True

                steps = 5000
                SORN_UI.network.simulate_iterations(steps, 100, measure_block_time=True)

                self.readout = train(SORN_UI.network['pediction_rec'], 'n.output', SORN_UI.network['index_rec', 0], 'n.pattern_index', 0, steps, lag=1)
                self.readout_simu = train_same_step(SORN_UI.network['pediction_rec'], 'n.output', SORN_UI.network['index_rec', 0], 'n.pattern_index', 0, steps)


                SORN_UI.network.remove_behaviours_from_neuron_groups(SORN_UI.network['prediction_source'], tags=['pediction_rec'])
                SORN_UI.network.remove_behaviours_from_neuron_groups(SORN_UI.network['text_input_group'], tags=['index_rec'])

                #SORN_UI.network.clear_recorder(['pediction_rec', 'index_rec'])
                #SORN_UI.network.deactivate_mechanisms(['pediction_rec', 'index_rec'])

                #SORN_UI.network.recording_on()

                print('training_finished')

            self.pred_text_label = QLabel(SORN_UI.main_window)
            SORN_UI.Add_Sidebar_Element(self.pred_text_label, stretch=0.2)
            self.pred_text_label.mousePressEvent = train_click
            self.pred_text_label.setText('Click to Train...')
            self.pred_text = list(self.pred_text_label.text())

            self.pred_simu_text_label = QLabel(SORN_UI.main_window)
            SORN_UI.Add_Sidebar_Element(self.pred_simu_text_label, stretch=0.2)
            self.pred_simu_text_label.mousePressEvent = train_click
            self.pred_simu_text_label.setText('Click to Train...')
            self.pred_simu_text = list(self.pred_simu_text_label.text())



    def update(self, SORN_UI):

        # save data timestep
        if not SORN_UI.update_without_state_change and SORN_UI.network['grammar_act', 0] is not None:

            grammar_act = SORN_UI.network['grammar_act', 0]

            if grammar_act is not None:
                self.inp_text_label.setText('I: ' + ''.join(self.text))
                if self.readout_simu is not None:
                    symbol_simu = predict_char(self.readout_simu, SORN_UI.network['prediction_source'], 'n.output')
                    char = grammar_act.index_to_char(symbol_simu)
                    self.pred_simu_text += char
                    self.pred_simu_text_label.setText('P_simu: ' + ''.join(self.pred_simu_text))

                if self.readout is not None:
                    symbol = predict_char(self.readout, SORN_UI.network['prediction_source'], 'n.output')
                    char = grammar_act.index_to_char(symbol)
                    self.pred_text += char
                    self.pred_text_label.setText('P: ' + ''.join(self.pred_text))

                if self.input_select_box.currentText() == 'Prediction':
                    if self.readout is not None:
                        grammar_act.set_next_char(char)
                        # self.network[self.exc_group_name, ts_group].input += self.network['grammar_act', 0].W[:, symbol]sdfdsfgdsfgdf
                    else:
                        print('warning: predictor not trained')

                if self.input_select_box.currentText() == 'Grammar Act.':
                    self.text.append(grammar_act.get_char())
                elif self.input_select_box.currentText() == 'Prediction' and self.readout is not None:
                    self.text.append(char)
                else:
                    self.text.append('|')

            if len(self.text) > 40: self.text.pop(0)
            if len(self.pred_text) > 40: self.pred_text.pop(0)
            if len(self.pred_simu_text) > 40: self.pred_simu_text.pop(0)

