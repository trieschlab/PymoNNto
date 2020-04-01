from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg

from Testing.SORN.SORN_Helper import *

class SORN_UI_sidebar_fast_forward():

    def add_recorder_variables(self, neuron_group, recorder):
        return

    def recorder_on_off(self, SORN_UI, enable):
        for rec in SORN_UI.network['UI_rec']:
            rec.behaviour_enabled = enable or self.rec_cb.isChecked()

    def initialize(self, SORN_UI):

        def start_pause_click(event):
            SORN_UI.pause = not SORN_UI.pause

        self.sp_btn = QPushButton('start/pause', SORN_UI.main_window)
        self.sp_btn.clicked.connect(start_pause_click)
        SORN_UI.Add_Sidebar_Element(self.sp_btn)

        self.rec_cb = QCheckBox()
        self.rec_cb.setText('ff record')
        self.rec_cb.setChecked(False)
        SORN_UI.Add_Sidebar_Element(self.rec_cb)

        h_layout = SORN_UI.Add_Sidebar_Element(return_h_layout=True)

        SORN_UI.step = False

        def one_step(event):
            SORN_UI.step = True

        self.os_btn = QPushButton('1 step', SORN_UI.main_window)
        self.os_btn.clicked.connect(one_step)
        # self.Add_Sidebar_Element(self.os_btn)
        h_layout.addWidget(self.os_btn)

        def fast_forward(event):
            self.recorder_on_off(SORN_UI, False)
            SORN_UI.network.simulate_iterations(100, 100, measure_block_time=True)
            self.recorder_on_off(SORN_UI, True)

        self.ff_btn = QPushButton('100', SORN_UI.main_window)
        self.ff_btn.clicked.connect(fast_forward)
        # self.Add_Sidebar_Element(self.ff_btn)
        h_layout.addWidget(self.ff_btn)

        def fast_forward(event):
            self.recorder_on_off(SORN_UI, False)
            SORN_UI.network.simulate_iterations(1000, 100, measure_block_time=True)
            self.recorder_on_off(SORN_UI, True)

        self.ff_btn = QPushButton('1k', SORN_UI.main_window)
        self.ff_btn.clicked.connect(fast_forward)
        # self.Add_Sidebar_Element(self.ff_btn)
        h_layout.addWidget(self.ff_btn)

        h_layout = SORN_UI.Add_Sidebar_Element(return_h_layout=True)

        def fast_forward(event):
            self.recorder_on_off(SORN_UI, False)
            SORN_UI.network.simulate_iterations(5000, 100, measure_block_time=True)
            self.recorder_on_off(SORN_UI, True)

        self.ff_btn = QPushButton('5k', SORN_UI.main_window)
        self.ff_btn.clicked.connect(fast_forward)
        # self.Add_Sidebar_Element(self.ff_btn)
        h_layout.addWidget(self.ff_btn)

        def fast_forward(event):
            self.recorder_on_off(SORN_UI, False)
            SORN_UI.network.simulate_iterations(15000, 100, measure_block_time=True)
            self.recorder_on_off(SORN_UI, True)

        self.ff_btn = QPushButton('15k', SORN_UI.main_window)
        self.ff_btn.clicked.connect(fast_forward)
        # self.Add_Sidebar_Element(self.ff_btn)
        h_layout.addWidget(self.ff_btn)

        def fast_forward(event):
            self.recorder_on_off(SORN_UI, False)
            SORN_UI.network.simulate_iterations(50000, 100, measure_block_time=True)
            self.recorder_on_off(SORN_UI, True)

        self.ff_btn = QPushButton('50k', SORN_UI.main_window)
        self.ff_btn.clicked.connect(fast_forward)
        # self.Add_Sidebar_Element(self.ff_btn)
        h_layout.addWidget(self.ff_btn)

    def update(self, SORN_UI):
        return