from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg

#from Testing.SORN.SORN_Helper import *
from NetworkBehaviour.Recorder.Recorder import *
#from Testing.Common.Classifier_Helper import *
from Testing.Common.Grammar_Helper import *

class sidebar_grammar_module():

    def __init__(self, next_p=True, simu_p=True, noc_p=True, text_length=35):
        self.next_p=next_p
        self.simu_p=simu_p
        self.noc_p=noc_p
        self.text_length=text_length


    def add_recorder_variables(self, neuron_group, Network_UI):
        return
        #if hasattr(neuron_group, 'output'):
        #    Network_UI.add_recording_variable(neuron_group, 'n.output', timesteps=100)

    def initialize(self, Network_UI):
        if Network_UI.network['grammar_act', 0] is not None:

            self.grammar_tab = Network_UI.Next_Tab('text analysis')

            self.readout = None
            self.readout_simu = None

            # self.Add_Sidebar_Spacing()

            def learning_on_off(event):
                Network_UI.network.set_mechanisms(['STDP'], self.stdp_cb.isChecked())

            self.stdp_cb = QCheckBox()
            self.stdp_cb.setText('STDP')
            self.stdp_cb.setChecked(True)
            self.stdp_cb.stateChanged.connect(learning_on_off)
            Network_UI.Add_Sidebar_Element(self.stdp_cb)

            def grammar_activator_on_off(event):
                Network_UI.network['grammar_act', 0].active = self.input_select_box.currentText() != 'None'

            self.input_select_box = QComboBox()
            self.input_select_box.addItem("Grammar Act.")
            self.input_select_box.addItem("Prediction")
            self.input_select_box.addItem("None")
            self.input_select_box.currentIndexChanged.connect(grammar_activator_on_off)
            self.input_select_box.setToolTip('select which input is fed into the network')
            Network_UI.Add_Sidebar_Element(self.input_select_box)

            self.inp_text_label = QLabel(Network_UI.main_window)
            Network_UI.Add_Sidebar_Element(self.inp_text_label, stretch=0.2)
            self.inp_text_label.setText('')
            self.inp_text_label.setToolTip('current network input')
            self.text = []

            def train_click(event):

                item = pg.InfiniteLine(pos=Network_UI.network.iteration, movable=False, angle=90)
                self.wnr_plot.addItem(item)

                #Network_UI.network.deactivate_mechanisms('STDP')

                #Network_UI.network.recording_off()

                Network_UI.network.add_behaviours_to_neuron_groups({100: NeuronRecorder(['n.output'], tag='pediction_rec')}, Network_UI.network['prediction_source'])
                Network_UI.network.add_behaviours_to_neuron_groups({101: NeuronRecorder(['n.pattern_index'], tag='index_rec')}, Network_UI.network['text_input_group'])

                #for ng in Network_UI.network['prediction_source']:
                #    Network_UI.network.add_behaviours_to_neuron_group({100: NeuronRecorder(['n.output'], tag='pediction_rec')}, ng)
                #for ng in Network_UI.network['text_input_group']:
                #    Network_UI.network.add_behaviours_to_neuron_group({101: NeuronRecorder(['n.pattern_index'], tag='index_rec')}, ng)


                Network_UI.network['grammar_act', 0].active = True

                steps = 5000
                Network_UI.network.simulate_iterations(steps, 100, measure_block_time=True)

                if self.next_p:
                    self.readout = train(Network_UI.network['pediction_rec'], 'n.output', Network_UI.network['index_rec', 0], 'n.pattern_index', 0, steps, lag=1)

                if self.simu_p:
                    self.readout_simu = train_same_step(Network_UI.network['pediction_rec'], 'n.output', Network_UI.network['index_rec', 0], 'n.pattern_index', 0, steps)


                Network_UI.network.remove_behaviours_from_neuron_groups(Network_UI.network['prediction_source'], tags=['pediction_rec'])
                Network_UI.network.remove_behaviours_from_neuron_groups(Network_UI.network['text_input_group'], tags=['index_rec'])

                #Network_UI.network.clear_recorder(['pediction_rec', 'index_rec'])
                #Network_UI.network.deactivate_mechanisms(['pediction_rec', 'index_rec'])

                #Network_UI.network.recording_on()

                #Network_UI.network.activate_mechanisms('STDP')

                self.input_select_box.setCurrentIndex(1)

                print('training_finished')

                item = pg.InfiniteLine(pos=Network_UI.network.iteration, movable=False, angle=90)
                self.wnr_plot.addItem(item)

                item = pg.InfiniteLine(pos=Network_UI.network.iteration+1000, movable=False, angle=90)
                self.wnr_plot.addItem(item)

            if self.noc_p:
                self.noc_text_label = QLabel(Network_UI.main_window)
                Network_UI.Add_Sidebar_Element(self.noc_text_label, stretch=0.2)
                self.noc_text = list(self.noc_text_label.text())
                self.noc_text_label.setToolTip('most active input neuron character')


            if self.next_p:
                self.pred_text_label = QLabel(Network_UI.main_window)
                Network_UI.Add_Sidebar_Element(self.pred_text_label, stretch=0.2)
                self.pred_text_label.mousePressEvent = train_click
                self.pred_text_label.setText('Click to Train...')
                self.pred_text = list(self.pred_text_label.text())
                self.pred_text_label.setToolTip('classifiers prediction for next timesteps (can be fed back into the network)')

            if self.simu_p:
                self.pred_simu_text_label = QLabel(Network_UI.main_window)
                Network_UI.Add_Sidebar_Element(self.pred_simu_text_label, stretch=0.2)
                self.pred_simu_text_label.mousePressEvent = train_click
                self.pred_simu_text_label.setText('Click to Train...')
                self.pred_simu_text = list(self.pred_simu_text_label.text())
                self.pred_simu_text_label.setToolTip('classifiers prediction for current timestep')

            self.text_box = QTextEdit()

            #self.highlighter = Highlighter(self.editor.document())
            #self.editor.setText(sample)
            #layout = QtGui.QVBoxLayout(self)
            #layout.addWidget(self.editor)

            Network_UI.Add_element(self.text_box)
            self.noc_text_long = ''


            self.wnr_tab = Network_UI.Next_Tab('WNR')

            btn = QPushButton('train')
            btn.mousePressEvent = train_click
            Network_UI.Add_element(btn)

            _, self.wnr_bar_plot = Network_UI.Add_plot_curve('Wrong/New/Right Sentences', True, False, legend=False,x_label='', y_label='')

            Network_UI.Next_H_Block()

            self.wrong_s = []
            self.new_s = []
            self.right_s = []
            self.iteration_list = []
            self.wnr_curves, self.wnr_plot = Network_UI.Add_plot_curve('Wrong/New/Right Sentences', True, False, number_of_curves=3, legend=False, x_label='', y_label='', colors=['r', (255,150,0), 'g'])



    def update(self, Network_UI):

        # save data timestep
        if not Network_UI.update_without_state_change and Network_UI.network['grammar_act', 0] is not None:

            grammar_act = Network_UI.network['grammar_act', 0]

            if grammar_act is not None:
                self.inp_text_label.setText('I: ' + ''.join(self.text[-self.text_length:]))

                self.noc_text_label.setText('NC: ' + ''.join(self.noc_text[-self.text_length:]))

                char_act = np.zeros(len(grammar_act.alphabet))
                for ng in Network_UI.network['prediction_source']:
                    recon = ng.Input_Weights.transpose().dot(ng.output)
                    char_act += recon
                char = grammar_act.index_to_char(np.argmax(char_act))

                self.noc_text.append(char)
                self.noc_text_long += char
                if self.grammar_tab.isVisible():
                    self.text_box.setText(grammar_act.mark_with_grammar(self.noc_text_long, False))

                if self.readout_simu is not None:
                    symbol_simu = predict_char(self.readout_simu, Network_UI.network['prediction_source'], 'n.output')
                    char = grammar_act.index_to_char(symbol_simu)
                    self.pred_simu_text += char
                    self.pred_simu_text_label.setText('PC: ' + ''.join(self.pred_simu_text[-self.text_length:]))

                if self.readout is not None:
                    symbol = predict_char(self.readout, Network_UI.network['prediction_source'], 'n.output')
                    char = grammar_act.index_to_char(symbol)
                    self.pred_text += char
                    self.pred_text_label.setText('PN: ' + ''.join(self.pred_text[-self.text_length:]))

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


            if Network_UI.network.iteration%10 and self.wnr_tab.isVisible():
                score_info = grammar_act.get_text_score(''.join(self.pred_text))

                n_sentences = score_info['n_output_sentences']
                if n_sentences>0:
                    w = score_info['n_wrong_sentences']/n_sentences
                    n = score_info['n_new_sentences']/n_sentences
                    r = score_info['n_right_sentences']/n_sentences

                    self.wrong_s.append(w)
                    self.new_s.append(n)
                    self.right_s.append(r)
                    self.iteration_list.append(Network_UI.network.iteration)

                    self.wnr_curves[0].setData(self.iteration_list, self.wrong_s)
                    self.wnr_curves[1].setData(self.iteration_list, self.new_s)
                    self.wnr_curves[2].setData(self.iteration_list, self.right_s)

                    self.wnr_bar_plot.clear()
                    self.wnr_bar_item = pg.BarGraphItem(x=[1, 2, 3], height=[w, n, r], width=0.6, brushes=['r', (255,150,0), 'g'])
                    self.wnr_bar_plot.addItem(self.wnr_bar_item)

                #self.isi_plt.clear()
                #y, x = np.histogram(SpikeTrain_ISI(self.neuron_act_data), bins=15)
                #curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=Network_UI.neuron_select_color)
                #self.isi_plt.addItem(curve)

                #if len(self.wrong_s) > 1000: self.wrong_s.pop(0)
                #if len(self.new_s) > 1000: self.new_s.pop(0)
                #if len(self.right_s) > 1000: self.right_s.pop(0)
                #if len(self.iteration_list) > 1000: self.iteration_list.pop(0)

            if len(self.text) > 1000: self.text.pop(0)
            if len(self.pred_text) > 1000: self.pred_text.pop(0)
            if len(self.pred_simu_text) > 1000: self.pred_simu_text.pop(0)



