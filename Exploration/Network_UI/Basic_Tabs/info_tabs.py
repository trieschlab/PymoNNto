from PymoNNto.Exploration.Network_UI.TabBase import *


class info_tab(TabBase):

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def initialize(self, Network_UI):

        Network_UI.infotabs=[]

        for group in Network_UI.network.NeuronGroups:
            self.make_group_tab(Network_UI, [group])

        temp = {}
        for g in Network_UI.network.SynapseGroups:
            key = ','.join(g.tags)
            if key not in temp:
                temp[key] = [g]
            else:
                temp[key].append(g)

        for k in temp:
            self.make_group_tab(Network_UI, temp[k])



    def make_group_tab(self, Network_UI, groups):
        title = '[' + str(groups[0].tags[0]) + ']'
        if len(groups)>1:
            title+=' (Partitioned)'
        infotab = Network_UI.Next_Tab(title)

        Network_UI.infotabs.append(infotab)

        h = 0

        caption = QLabel(str(groups[0].tags[0]) + ':')
        caption.setFont(QFont('SansSerif', 16))
        h += 40
        Network_UI.Add_element(caption)
        Network_UI.Next_H_Block()

        for key in groups[0].behaviour:
            main_tag = groups[0].behaviour[key].tags[0]

            behaviours = [g.behaviour[key] for g in groups]

            self.add_line(Network_UI, str(key) + ' ' + main_tag, behaviours, groups)
            h += 60

        infotab.setMaximumHeight(h)

    def add_line(self, Network_UI, text, behaviours=None, groups=None):

        element = QCheckBox()
        element.setChecked(behaviours[0].behaviour_enabled)
        element.setText(text)

        def click(event):
            for behaviour in behaviours:
                behaviour.behaviour_enabled = element.isChecked()

        def cut_length(s):
            result = ''
            for i, c in enumerate(s):
                result += c
                if i % 80 == 79:
                    result += '\r\n'
            return result

        element.stateChanged.connect(click)
        element2 = QLabel(cut_length(str(behaviours[0].init_kwargs)))

        container = QVBoxLayout()  # self.main_window

        def addArg(arg):
            h_container = QHBoxLayout()
            h_container.addWidget(QLabel(arg), stretch=1)

            edit = QLineEdit(str(behaviours[0].init_kwargs[arg]))
            edit.arg = arg

            def change_param(event):
                for behaviour in behaviours:
                    behaviour.init_kwargs[edit.arg] = edit.text()

            edit.textChanged.connect(change_param)

            h_container.addWidget(edit, stretch=1)
            h_container.addWidget(QLabel(''), stretch=5)
            container.addLayout(h_container)

        for arg in behaviours[0].init_kwargs:
            addArg(arg)

        def update(event):
            for neurons,behaviour in zip(groups, behaviours):
                behaviour.set_variables(neurons)
                element2.setText(cut_length(str(behaviour.init_kwargs)))

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

        if not 'structure' in behaviours[0].tags:
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

    def update(self, Network_UI):
        return