from PymoNNto.Exploration.Network_UI.TabBase import *


class sidebar_fast_forward_module(TabBase):

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def recorder_on_off(self, Network_UI, enable):
        for rec in Network_UI.network['UI_rec']:
            rec.behaviour_enabled = enable or self.rec_cb.isChecked()

    def initialize(self, Network_UI):
        self.iteration_display_label=Network_UI.Add_element(QLabel(),sidebar=True)
        self.iteration_display_label.setMaximumHeight(10)

        def start_pause_click(event):
            Network_UI.pause = not Network_UI.pause

        self.sp_btn = QPushButton('start/pause', Network_UI.main_window)
        self.sp_btn.clicked.connect(start_pause_click)
        Network_UI.Add_Sidebar_Element(self.sp_btn)

        h_layout = Network_UI.Add_Sidebar_Element(return_h_layout=True)
        h_layout.addWidget(QLabel('Render every X frames.'))
        self.render_every_x_frames_spin = QSpinBox()
        self.render_every_x_frames_spin.setMinimum(1)
        self.render_every_x_frames_spin.setMaximum(1000)

        def change_rexf(event):
            Network_UI.render_every_x_frames = self.render_every_x_frames_spin.value()

        self.render_every_x_frames_spin.valueChanged.connect(change_rexf)

        h_layout.addWidget(self.render_every_x_frames_spin)

        if Network_UI.storage_manager is not None:
            self.record_frames_cb=QCheckBox('save frames')
            def cb_state_changed(event):
                if not self.record_frames_cb.isChecked():
                    dlg = QDialog()
                    dlg.setWindowTitle("Do you want to render a video?")
                    layout = QVBoxLayout()

                    path_tl=QLineEdit(Network_UI.storage_manager.absolute_path)
                    path_tl.setReadOnly(True)
                    layout.addWidget(path_tl)

                    delete_frames_cb = QCheckBox('delete frame images')
                    layout.addWidget(delete_frames_cb)

                    def render():
                        Network_UI.storage_manager.render_video('ui_frame_', delete_images=delete_frames_cb.isChecked())
                        dlg.close()


                    render_btn = QPushButton('render video')
                    render_btn.clicked.connect(render)

                    layout.addWidget(render_btn)
                    dlg.setLayout(layout)
                    dlg.resize(300, 50)
                    dlg.exec()

            self.record_frames_cb.stateChanged.connect(cb_state_changed)
            h_layout.addWidget(self.record_frames_cb)

        line=Network_UI.Add_element(QFrame(),sidebar=True)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)


        h_layout = Network_UI.Add_Sidebar_Element(return_h_layout=True)

        Network_UI.step = False

        def one_step(event):
            Network_UI.step = True

        self.os_btn = QPushButton('X steps', Network_UI.main_window)
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

        self.rec_cb = QCheckBox()
        self.rec_cb.setText('fast forward record')
        self.rec_cb.setChecked(False)
        Network_UI.Add_Sidebar_Element(self.rec_cb)

        line=Network_UI.Add_element(QFrame(),sidebar=True)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

    def record_frame(self, Network_UI):
        if Network_UI.storage_manager is not None:
            pix = QtGui.QPixmap(Network_UI.main_window.size())
            Network_UI.main_window.render(pix)
            file_path=Network_UI.storage_manager.get_next_frame_name('ui_frame_')
            pix.save(file_path)

    def update(self, Network_UI):

        self.iteration_display_label.setText('Iteration: '+str(Network_UI.network.iteration))

        if self.record_frames_cb.isChecked():
            self.record_frame(Network_UI)
