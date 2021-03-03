from PymoNNto.Exploration.Network_UI.TabBase import *


class info_tab(TabBase):

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def initialize(self, Network_UI):

        def add_line(text, behaviour=None, neurons=None):

            element = QCheckBox()
            element.setChecked(behaviour.behaviour_enabled)
            element.setText(text)

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

            if not 'structure' in behaviour.tags:
                element2.mousePressEvent = hide_show
                link_font = QFont()  # 'SansSerif', 12
                link_font.setUnderline(True)
                # palette = QPalette()
                # palette.setColor(QPalette.Text, QtCore.Qt.blue)
                # element2.setPalette(palette)
                element2.setFont(link_font)
                element2.setStyleSheet("color: rgb(0,0,200)")


            Network_UI.Add_element(element)
            Network_UI.Add_element(element2, stretch=5)
            Network_UI.Next_H_Block()
            # self.current_H_block.addLayout(container)

            Network_UI.Add_element(frame)
            Network_UI.Next_H_Block()

        Network_UI.infotabs=[]

        for group in Network_UI.network.NeuronGroups:
            infotab = Network_UI.Next_Tab('Info: ' + str(group.tags[0]))
            Network_UI.infotabs.append(infotab)

            h = 0

            caption = QLabel(str(group.tags[0]) + ':')
            caption.setFont(QFont('SansSerif', 16))
            h += 40
            Network_UI.Add_element(caption)
            Network_UI.Next_H_Block()
            for key in group.behaviour:
                behaviour = group.behaviour[key]
                main_tag = ''
                if len(behaviour.tags)>0:
                    main_tag = behaviour.tags[0]
                add_line(str(key) + ' ' + main_tag, behaviour, group)
                h += 60

            infotab.setMaximumHeight(h)


    def update(self, Network_UI):
        return