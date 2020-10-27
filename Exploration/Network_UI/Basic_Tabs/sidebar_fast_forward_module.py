from SORNSim.Exploration.Network_UI.TabBase import *


class sidebar_fast_forward_module(TabBase):

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def recorder_on_off(self, Network_UI, enable):
        for rec in Network_UI.network['UI_rec']:
            rec.behaviour_enabled = enable or self.rec_cb.isChecked()

    def initialize(self, Network_UI):

        def start_pause_click(event):
            Network_UI.pause = not Network_UI.pause

        self.sp_btn = QPushButton('start/pause', Network_UI.main_window)
        self.sp_btn.clicked.connect(start_pause_click)
        Network_UI.Add_Sidebar_Element(self.sp_btn)

        self.rec_cb = QCheckBox()
        self.rec_cb.setText('fast forward record')
        self.rec_cb.setChecked(False)
        Network_UI.Add_Sidebar_Element(self.rec_cb)

        h_layout = Network_UI.Add_Sidebar_Element(return_h_layout=True)

        Network_UI.step = False

        def one_step(event):
            Network_UI.step = True

        self.os_btn = QPushButton('1 step', Network_UI.main_window)
        self.os_btn.clicked.connect(one_step)
        # self.Add_Sidebar_Element(self.os_btn)
        h_layout.addWidget(self.os_btn)

        def fast_forward(event):
            self.recorder_on_off(Network_UI, False)
            Network_UI.network.simulate_iterations(100, 100, measure_block_time=True)
            self.recorder_on_off(Network_UI, True)

        self.ff_btn = QPushButton('100', Network_UI.main_window)
        self.ff_btn.clicked.connect(fast_forward)
        # self.Add_Sidebar_Element(self.ff_btn)
        h_layout.addWidget(self.ff_btn)

        def fast_forward(event):
            self.recorder_on_off(Network_UI, False)
            Network_UI.network.simulate_iterations(1000, 100, measure_block_time=True)
            self.recorder_on_off(Network_UI, True)

        self.ff_btn = QPushButton('1k', Network_UI.main_window)
        self.ff_btn.clicked.connect(fast_forward)
        # self.Add_Sidebar_Element(self.ff_btn)
        h_layout.addWidget(self.ff_btn)

        h_layout = Network_UI.Add_Sidebar_Element(return_h_layout=True)

        def fast_forward(event):
            self.recorder_on_off(Network_UI, False)
            Network_UI.network.simulate_iterations(5000, 100, measure_block_time=True)
            self.recorder_on_off(Network_UI, True)

        self.ff_btn = QPushButton('5k', Network_UI.main_window)
        self.ff_btn.clicked.connect(fast_forward)
        # self.Add_Sidebar_Element(self.ff_btn)
        h_layout.addWidget(self.ff_btn)

        def fast_forward(event):
            self.recorder_on_off(Network_UI, False)
            Network_UI.network.simulate_iterations(15000, 100, measure_block_time=True)
            self.recorder_on_off(Network_UI, True)

        self.ff_btn = QPushButton('15k', Network_UI.main_window)
        self.ff_btn.clicked.connect(fast_forward)
        # self.Add_Sidebar_Element(self.ff_btn)
        h_layout.addWidget(self.ff_btn)

        def fast_forward(event):
            self.recorder_on_off(Network_UI, False)
            Network_UI.network.simulate_iterations(50000, 100, measure_block_time=True)
            self.recorder_on_off(Network_UI, True)

        self.ff_btn = QPushButton('50k', Network_UI.main_window)
        self.ff_btn.clicked.connect(fast_forward)
        # self.Add_Sidebar_Element(self.ff_btn)
        h_layout.addWidget(self.ff_btn)

    def update(self, SORN_UI):
        return