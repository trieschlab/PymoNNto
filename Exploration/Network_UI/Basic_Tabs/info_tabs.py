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
        infotab = Network_UI.add_tab(title=title) #Network_UI.Next_Tab(title)

        Network_UI.infotabs.append(infotab)

        h = 0

        caption = QLabel(str(groups[0].tags[0]) + ':')
        caption.setFont(QFont('SansSerif', 16))
        h += 240
        Network_UI.tab.add_widget(caption)
        Network_UI.tab.add_row()

        for key in groups[0].behavior:
            main_tag = groups[0].behavior[key].tags[0]

            behaviors = [g.behavior[key] for g in groups]

            self.add_line(Network_UI, str(key) + ' ' + main_tag, behaviors, groups)
            h += 60

        infotab.setMaximumHeight(h)

    def add_line(self, Network_UI, text, behaviors=None, groups=None):

        element = QCheckBox()
        element.setChecked(behaviors[0].behavior_enabled)
        element.setText(text)

        def click(event):
            for behavior in behaviors:
                behavior.behavior_enabled = element.isChecked()
                Network_UI.add_event(behavior.tags[0]+' ('+str(element.isChecked())+')')

        def cut_length(s):
            result = ''
            for i, c in enumerate(s):
                result += c
                if i % 80 == 79:
                    result += '\r\n'
            return result

        element.stateChanged.connect(click)
        element2 = QLabel(cut_length(str(behaviors[0].init_kwargs)))

        container = QVBoxLayout()  # self.main_window

        def addArg(arg):
            h_container = QHBoxLayout()
            h_container.addWidget(QLabel(arg), stretch=1)

            edit = QLineEdit(str(behaviors[0].init_kwargs[arg]))
            edit.arg = arg

            def change_param(event):
                for behavior in behaviors:
                    behavior.init_kwargs[edit.arg] = edit.text()

            edit.textChanged.connect(change_param)

            h_container.addWidget(edit, stretch=1)
            h_container.addWidget(QLabel(''), stretch=5)
            container.addLayout(h_container)






        plot_data_list = behaviors[0].get_UI_Preview_Plots()
        if plot_data_list is not None:
            h_container = QHBoxLayout()

            for temp in plot_data_list:
                try:
                    plot_data = np.array(temp)

                    canvas = pg.GraphicsLayoutWidget()
                    canvas.ci.layout.setContentsMargins(0, 0, 0, 0)
                    canvas.ci.layout.setSpacing(0)
                    canvas.setMaximumWidth(200)
                    canvas.setAlignment(Qt.AlignLeft)
                    canvas.setBackground((255, 255, 255))
                    plt = canvas.addPlot(row=0, col=0)

                    if plot_data.ndim==1:#y
                        curve = pg.PlotCurveItem(y=plot_data,pen=(50,50,50,255))
                        plt.addItem(curve)
                    elif plot_data.ndim==2:#x y
                        curve = pg.PlotCurveItem(x=plot_data[0],y=plot_data[1],pen=(50,50,50,255))
                        plt.addItem(curve)
                    elif plot_data.ndim>=2 and plot_data.shape[0]>2:#image
                        plt.hideAxis('left')
                        plt.hideAxis('bottom')
                        image_item = pg.ImageItem(plot_data)
                        plt.addItem(image_item)
                except Exception as e:
                    print(e)

                h_container.addWidget(canvas, stretch=7)

            h_container.setAlignment(Qt.AlignLeft)
            container.addLayout(h_container)
            #curve.setData(x=list(range(len(plot_data))),y=plot_data)


        for arg in behaviors[0].init_kwargs:
            addArg(arg)

        def update(event):
            for neurons,behavior in zip(groups, behaviors):
                behavior.initialize(neurons)
                element2.setText(cut_length(str(behavior.init_kwargs)))

        h_container = QHBoxLayout()
        btn = QPushButton('update')
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

        if not 'structure' in behaviors[0].tags:
            element2.mousePressEvent = hide_show
            link_font = QFont()  # 'SansSerif', 12
            link_font.setUnderline(True)
            element2.setFont(link_font)
            element2.setStyleSheet("color: rgb(0,0,200)")

        Network_UI.tab.add_widget(element)
        Network_UI.tab.add_widget(element2, stretch=500)
        Network_UI.tab.add_row()

        Network_UI.tab.add_widget(frame)
        Network_UI.tab.add_row()

    def update(self, Network_UI):
        return