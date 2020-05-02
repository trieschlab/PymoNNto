from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np

class stdp_buffer_tab():

    def __init__(self, title='STDP'):
        self.title = title

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def initialize(self, Network_UI):
        self.stdp_tab = Network_UI.Next_Tab(self.title)#, create_h_block=False

        Network_UI.Add_element(QLabel('Select syn'), stretch=0)
        self.select_syn_box = QComboBox()
        self.select_syn_box.addItems(Network_UI.transmitters)
        self.select_syn_box.setCurrentIndex(0)
        Network_UI.Add_element(self.select_syn_box, stretch=4)

        Network_UI.Next_H_Block(stretch=10)

        grid_base_widget=QWidget()
        Network_UI.Add_element(grid_base_widget)


        grid_layout = QGridLayout(grid_base_widget)
        #Network_UI.visualization_layout.addLayout(grid_layout)

        self.syn_canvas = pg.GraphicsLayoutWidget()

        self.syn_canvas.setBackground((255, 255, 255))
        self.syn_plot = self.syn_canvas.addPlot(row=0, col=0)
        self.syn_plot.setToolTip('Synaptic change from STDP (gray=no change, black=shrink, white=grow)')
        self.syn_plot.setLabels(title='Delta W')
        #self.syn_plot.hideAxis('left')
        #self.syn_plot.hideAxis('bottom')
        self.syn_img = pg.ImageItem(np.random.rand(291, 291, 3))
        self.syn_plot.addItem(self.syn_img)
        grid_layout.addWidget(self.syn_canvas, 0, 0)

        def update():
            base_rect = self.syn_plot.viewRect()
            self.pre_plot.setRange(QtCore.QRectF(base_rect.x(), 0, base_rect.width(), self.pre_length), padding=0)  #
            self.post_plot.setRange(QtCore.QRectF(0, base_rect.y(), self.post_length, base_rect.height()), padding=0)  #
            self.syn_plot.disableAutoRange()
            self.pre_plot.disableAutoRange()
            self.post_plot.disableAutoRange()

        old_wheel_event=self.syn_canvas.wheelEvent
        def wheel(event):
            old_wheel_event(event)
            update()
        self.syn_canvas.wheelEvent=wheel

        old_move_event=self.syn_canvas.mouseMoveEvent
        def move(event):
            old_move_event(event)
            update()
        self.syn_canvas.mouseMoveEvent=move

        self.pre_canvas = pg.GraphicsLayoutWidget()
        self.pre_canvas.setBackground((255, 255, 255))
        self.pre_plot = self.pre_canvas.addPlot(row=0, col=0)
        self.pre_plot.setToolTip('Pre Synaptic Activity')
        self.pre_plot.setLabels(title='Pre Act Buf')
        #self.pre_plot.hideAxis('left')
        #self.pre_plot.hideAxis('bottom')
        self.pre_img = pg.ImageItem(np.random.rand(291, 291, 3))
        self.pre_plot.addItem(self.pre_img)
        grid_layout.addWidget(self.pre_canvas, 1, 0)

        self.post_canvas = pg.GraphicsLayoutWidget()

        self.post_canvas.setBackground((255, 255, 255))
        self.post_plot = self.post_canvas.addPlot(row=0, col=0)
        self.post_plot.setToolTip('Post Synaptic Activity')
        self.post_plot.setLabels(title='Post Act Buf')
        #self.post_plot.hideAxis('left')
        #self.post_plot.hideAxis('bottom')
        self.post_img = pg.ImageItem(np.random.rand(291, 291, 3))
        self.post_plot.addItem(self.post_img)
        grid_layout.addWidget(self.post_canvas, 0, 1)

        grid_layout.setColumnStretch(0, 10)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setRowStretch(0, 6)
        grid_layout.setRowStretch(1, 1)

        Network_UI.Next_H_Block(stretch=0)

        qc = QCheckBox('Axis')
        def change(event):
            axis_enabeled = qc.isChecked()
            self.syn_plot.showAxis('left', axis_enabeled)
            self.syn_plot.showAxis('bottom', axis_enabeled)
            self.pre_plot.showAxis('left',axis_enabeled )
            self.pre_plot.showAxis('bottom', axis_enabeled)
            self.post_plot.showAxis('left', axis_enabeled)
            self.post_plot.showAxis('bottom', axis_enabeled)
        qc.setChecked(False)
        change(None)
        qc.stateChanged.connect(change)
        Network_UI.Add_element(qc)

        self.sensitivity_slider = QSlider(1)
        self.sensitivity_slider.setMinimum(0)
        self.sensitivity_slider.setMaximum(100)
        self.sensitivity_slider.setSliderPosition(50)
        Network_UI.Add_element(self.sensitivity_slider)

    def get_shift_and_zoom(self, transform):
        zero = QtCore.QPointF(0, 0)
        p = QtCore.QPointF(1, 1)
        zero_t = transform.map(zero)
        p_t = transform.map(p)
        x_shift = zero_t.x()
        y_shift = zero_t.y()
        x_zoom = p_t.x() - x_shift
        y_zoom = p_t.y() - y_shift
        return x_shift, y_shift, x_zoom, y_zoom

    def update(self, Network_UI):
        if self.stdp_tab.isVisible():
            if len(Network_UI.network[Network_UI.neuron_select_group]) > 0:
                group = Network_UI.network[Network_UI.neuron_select_group, 0]
                syn = group.afferent_synapses[self.select_syn_box.currentText()]
                if len(syn) > 0:
                    indx = 0
                    for i,s in enumerate(syn):
                        if type(s.dst.mask) == np.ndarray and s.dst.mask[Network_UI.neuron_select_id]:
                            indx=i
                    syn = syn[indx]

                    post_act = group.get_buffer(syn.dst, 'output', group.timescale)#s.dst.get_masked_dict('output_buffer_dict', neurons.timescale)
                    pre_act = group.get_buffer(syn.src, 'output', group.timescale)#s.src.get_masked_dict('output_buffer_dict', neurons.timescale)

                    self.post_length = len(post_act)
                    self.pre_length = len(pre_act)

                    sensitivity=self.sensitivity_slider.sliderPosition()/100.0*0.0001

                    self.pre_img.setImage(np.rot90(pre_act, 3), levels=(0, 1))
                    self.post_img.setImage(np.rot90(post_act.transpose(), 3), levels=(0, 1))

                    if hasattr(syn, 'dw'):
                        self.syn_img.setImage(np.rot90(syn.dw, 3), levels=(-sensitivity, +sensitivity))
                    else:
                        self.syn_img.clear()

            else:
                self.syn_img.clear()
                self.pre_img.clear()
                self.post_img.clear()

            '''
                    gap = 5
    
                    dwh = syn.dw.shape[0]
                    dww = syn.dw.shape[1]
    
                    syn.dw = np.concatenate([syn.dw, np.ones((syn.dw.shape[0], gap + len(post_act))) * -1], axis=1)
                    syn.dw = np.concatenate([syn.dw, np.ones((gap + len(pre_act), syn.dw.shape[1])) * -1], axis=0)
    
                    syn.dw[0:len(post_act[0]), dww + gap:dww + gap + len(post_act)] = post_act.transpose()
    
                    syn.dw[dwh + gap:dwh + gap + len(pre_act), 0:len(pre_act[0])] = pre_act
            '''




