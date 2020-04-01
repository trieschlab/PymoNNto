from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np


class SORN_info_tab():

    def add_recorder_variables(self, neuron_group, recorder):
        return

    def initialize(self, SORN_UI):

        def add_line(text, behaviour=None, neurons=None):

            element = QCheckBox()
            element.setChecked(behaviour.behaviour_enabled)

            def click(event):
                behaviour.behaviour_enabled = element.isChecked()
                # print(behaviour.tags, element.isChecked())

            element.stateChanged.connect(click)
            element2 = QLabel(str(behaviour.init_kwargs))

            container = QVBoxLayout()  # self.main_window

            def addArg(arg):
                h_container = QHBoxLayout()
                h_container.addWidget(QLabel(arg), stretch=1)

                edit = QLineEdit(str(behaviour.init_kwargs[arg]))
                edit.arg = arg

                def change_param(event):
                    behaviour.init_kwargs[edit.arg] = edit.text()

                edit.textChanged.connect(change_param)

                h_container.addWidget(edit, stretch=1)
                h_container.addWidget(QLabel(''), stretch=5)
                container.addLayout(h_container)

            for arg in behaviour.init_kwargs:
                addArg(arg)

            def update(event):
                behaviour.set_variables(neurons)
                element2.setText(str(behaviour.init_kwargs))

            h_container = QHBoxLayout()
            btn = QPushButton('update')  # , self.main_window
            btn.clicked.connect(update)
            h_container.addWidget(btn, stretch=2)
            h_container.addWidget(QLabel(''), stretch=5)
            container.addLayout(h_container)

            frame = QFrame()
            frame.setLayout(container)
            frame.hide()

            def hide_show(event):
                if frame.isVisible():
                    frame.hide()
                else:
                    frame.show()

            element2.mousePressEvent = hide_show

            element.setText(text)
            SORN_UI.Add_element(element)
            SORN_UI.Add_element(element2, stretch=5)
            SORN_UI.Next_H_Block()
            # self.current_H_block.addLayout(container)

            SORN_UI.Add_element(frame)
            SORN_UI.Next_H_Block()

        SORN_UI.infotabs=[]

        for group in SORN_UI.network.NeuronGroups:
            infotab = SORN_UI.Next_Tab('Info: ' + str(group.tags[0]))
            SORN_UI.infotabs.append(infotab)

            h = 0

            caption = QLabel(str(group.tags[0]) + ':')
            caption.setFont(QFont('SansSerif', 16))
            h += 40
            SORN_UI.Add_element(caption)
            SORN_UI.Next_H_Block()
            for key in group.behaviour:
                behaviour = group.behaviour[key]
                add_line(str(key) + ' ' + ' '.join(behaviour.tags[0]), behaviour, group)
                h += 60

            infotab.setMaximumHeight(h)


    def update(self, SORN_UI):
        return