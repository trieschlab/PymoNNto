from PymoNNto.Exploration.Network_UI.TabBase import *
from functools import partial

class sidebar_fast_forward_module(TabBase):

    def __init__(self, step_list=[100, 1000, 5000, 15000, 30000, 50000, 70000, 100000], title='PCA'):
        super().__init__(title)
        self.step_list = step_list

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def recorder_on_off(self, Network_UI, enable):
        for rec in Network_UI.network['UI_rec']:
            rec.behavior_enabled = enable or self.rec_cb.isChecked()

    def update_progress(self, progress, network=None):
        QApplication.instance().processEvents()
        self.progressbar.setValue(int(progress))

    def fast_forward(self, steps, Network_UI):

        Network_UI.add_event('fast forward', steps)

        self.update_progress(0)
        Network_UI.timer.stop()
        self.recorder_on_off(Network_UI, False)
        Network_UI.network.simulate_iterations(steps, 100, measure_block_time=True, batch_progress_update_func=self.update_progress)
        self.recorder_on_off(Network_UI, True)
        Network_UI.timer.start()

    def initialize(self, Network_UI):

        self.iteration_display_label=Network_UI.sidebar.add_widget(QLabel())
        self.iteration_display_label.setMaximumHeight(10)

        def start_pause_click(event):
            Network_UI.pause = not Network_UI.pause

        self.sp_btn = QPushButton('start/pause', Network_UI.main_window)
        self.sp_btn.clicked.connect(start_pause_click)
        Network_UI.sidebar.add_widget(self.sp_btn)

        Network_UI.sidebar.add_row()
        Network_UI.sidebar.add_widget(QLabel('Render every X frames.'))
        self.render_every_x_frames_spin = QSpinBox()
        self.render_every_x_frames_spin.setMinimum(1)
        self.render_every_x_frames_spin.setMaximum(1000)

        def change_rexf(event):
            Network_UI.render_every_x_frames = self.render_every_x_frames_spin.value()

        self.render_every_x_frames_spin.valueChanged.connect(change_rexf)

        Network_UI.sidebar.add_widget(self.render_every_x_frames_spin)

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
            Network_UI.sidebar.add_widget(self.record_frames_cb)

        Network_UI.sidebar.set_parent_layout()

        line=Network_UI.sidebar.add_widget(QFrame())
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)


        Network_UI.sidebar.add_row()

        Network_UI.step = False

        def one_step(event):
            Network_UI.step = True

        self.os_btn = QPushButton('X steps', Network_UI.main_window)
        self.os_btn.clicked.connect(one_step)
        Network_UI.sidebar.add_widget(self.os_btn)

        for i, steps in enumerate(self.step_list):

            if (i+1)%3==0:
                Network_UI.sidebar.add_row()

            def ff_btn_clicked(steps):
                self.fast_forward(steps, Network_UI)

            txt = str(steps)

            if steps%1000==0:
                txt=str(int(steps/1000))+'k'

            ff_btn = QPushButton(txt, Network_UI.main_window)
            ff_btn.clicked.connect(partial(ff_btn_clicked, steps))

            Network_UI.sidebar.add_widget(ff_btn)

        Network_UI.sidebar.set_parent_layout()

        self.rec_cb = Network_UI.sidebar.add_widget(QCheckBox())
        self.rec_cb.setText('fast forward record')
        self.rec_cb.setChecked(False)

        self.progressbar = Network_UI.sidebar.add_widget(QProgressBar())

        line = Network_UI.sidebar.add_widget(QFrame())
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

        if Network_UI.storage_manager is not None and self.record_frames_cb.isChecked():
            self.record_frame(Network_UI)
