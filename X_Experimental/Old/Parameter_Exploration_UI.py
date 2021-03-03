import matplotlib
matplotlib.use('Qt5Agg')

from Exploration.Old.Helper.Parameter_iterator import *

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from Exploration.UI_Base import *

class TREN_Parameter_Exploration_UI(UI_Base):

    def __init__(self, network, Neuron_Group, Input_Neuron_Group, param_list, label="Network_Test"):
        super().__init__(network, label=label)

        self.Neuron_Group = Neuron_Group
        self.Input_Neuron_Group = Input_Neuron_Group

        self.xsteps=10
        self.ysteps=6

        self.parameter_iterator = Parameter_iterator(self.On_PI_Iteration)

        if param_list is None:
            self.param_list=[]
            d = network.group_value_dicts[self.network.NeuronGroups[1]]
            for key in d:
                if not type(d[key]) == list and not type(d[key]) == dict and not key in ['learning', 'activity', 'avg_act', 'glu_inter_gamma_activity', 'GABA_inter_gamma_activity', 'height', 'depth', 'width', 'size', 'GLU_density', 'GABA_density', 'GLU_strength', 'GABA_strength', 'x', 'y', 'z']:
                    self.param_list.append(key)

            #for id in self.network.NeuronGroups[1].behaviours:
            #    for dict_self.network.NeuronGroups[1].behaviours[id].__dict__


            self.param_list.sort()
        else:
            self.param_list = param_list

        self.create_detail_label_pixmap()
        self.create_content_label_pixmap()

        self.init_QT_Elements()

        self.neu_rec = TRENRecorder_eval(['n.avg_act', 'n.norm_value', 'n.output_activity_history[0]', 'n.activity'], gapwidth=10)
        self.syn_rec = TRENSynapseRecorder_eval(['syn.GLU_Synapses'], gapwidth=100)

        network.add_behaviours_to_neuron_group([self.neu_rec, self.syn_rec], self.Neuron_Group)




    def add_param_block(self, param):
        self.label[param] = QLabel(self.main_window)
        self.label[param].setWordWrap(True)
        self.label[param].setText(param)


        value=self.network.NeuronGroups[1].get_modification_value(param)
        range_percentage = 0.5

        self.edits[param] = QLineEdit(self.main_window)
        self.edits[param].setText('{}'.format(value))


        def xset(event):
            self.xlabel.setText(param)
            self.xedit_min.setText('{}'.format(value*range_percentage))
            self.xedit_max.setText('{}'.format(value*(1+range_percentage)))

        def yset(event):
            self.ylabel.setText(param)
            self.yedit_min.setText('{}'.format(value*range_percentage))
            self.yedit_max.setText('{}'.format(value*(1+range_percentage)))

        self.xbtn[param] = QPushButton('x', self.main_window)
        self.xbtn[param].clicked.connect(xset)

        self.ybtn[param] = QPushButton('y', self.main_window)
        self.ybtn[param].clicked.connect(yset)

        self.Add_Sidebar_Element([self.label[param], self.edits[param], self.xbtn[param], self.ybtn[param]], [10,10,1,1])


    def init_QT_Elements(self):


        self.detail_qlabel.mousePressEvent = self.on_detail_click
        self.on_detail_click(None)

        self.Add_Sidebar_Spacing()

        self.label = {}
        self.edits = {}
        self.xbtn = {}
        self.ybtn = {}
        for param in self.param_list:
            self.add_param_block(param)

        self.Add_Sidebar_Spacing()

        self.xlabel = QLabel(self.main_window)
        self.xlabel.setWordWrap(True)
        self.xlabel.setText("x")

        self.xedit_min = QLineEdit(self.main_window)
        self.xedit_min.setText('')

        self.xedit_max = QLineEdit(self.main_window)
        self.xedit_max.setText('')

        self.Add_Sidebar_Element([self.xlabel,self.xedit_min, self.xedit_max])


        self.ylabel = QLabel(self.main_window)
        self.ylabel.setWordWrap(True)
        self.ylabel.setText('y')

        self.yedit_min = QLineEdit(self.main_window)
        self.yedit_min.setText('')

        self.yedit_max = QLineEdit(self.main_window)
        self.yedit_max.setText('')
        self.Add_Sidebar_Element([self.ylabel, self.yedit_min, self.yedit_max])



        block_add_btn = QPushButton('refresh', self.main_window)
        block_add_btn.clicked.connect(self.refresh_click)

        self.Add_Sidebar_Element(block_add_btn)


        self.content_qlabel.mousePressEvent = self.on_img_click


        #self.show()


    def On_PI_Iteration(self, axis):
        self.network.reset()

        for param in self.param_list:
            self.network.NeuronGroups[1].set_modification_value(param, float(self.edits[param].text()))

        self.network.NeuronGroups[1].set_modification_value(axis['x'].target_attribute_name, axis['x'].current_value)
        self.network.NeuronGroups[1].set_modification_value(axis['y'].target_attribute_name, axis['y'].current_value)

        print(axis['x'].target_attribute_name, axis['x'].current_value)
        print(axis['y'].target_attribute_name, axis['y'].current_value)

        for i in range(10000):
            self.network.simulate_iteration()
            #if i%500==0:


        xmax=len(axis['x'].values)*2
        ymax=len(axis['y'].values)*2
        xstep=axis['x'].step*2
        ystep=axis['y'].step*2

        self.draw_weights(xmax, ymax, xstep, ystep)

        def act_hist_plt(ax): ax.hist(np.array(self.neu_rec['n.activity'])[:, 0], bins=20)
        self.draw_pyplot(act_hist_plt, xmax, ymax, xstep+1, ystep, xlim=1)

        #def reward_hist_plt(ax): ax.hist(np.array(self.network.NeuronGroups[1][TRENRecorder].reward)[:, 0], bins=20)
        #self.draw_pyplot(reward_hist_plt, xmax, ymax, xstep+1, ystep+1,xlim=1)

        #print('f')

        #def norm_plt(ax): ax.plot(np.array(self.network.NeuronGroups[1][TRENRecorder].norm_value)[:, 0])
        #self.draw_pyplot(norm_plt, xmax, ymax, xstep, ystep+1)

        #print('gg')

    def on_detail_click(self, event):
        self.update_detail_image()
        qimg = self.numpy_array_to_qimage(get_reconstruction_activations(self.Input_Neuron_Group[TRENNeuronActivator].get_pattern_samples(50), 10, 10)*255, byte_count=1)
        self.draw_qimage(qimg, 0, 0, self.detail_pixmap.width(), self.detail_pixmap.height(), pixmap=self.detail_pixmap)
        if event is not None:
            self.refresh_img()

    def refresh_click(self, event):

        self.update_content_image()
        self.update_detail_image()

        x_param = self.xlabel.text()
        x_min = float(self.xedit_min.text())
        x_max = float(self.xedit_max.text())
        self.parameter_iterator.set_axis_steps('x', self.network.NeuronGroups[1], x_param, x_min, x_max, self.xsteps, False)#'post_learn_value', 0.0005, 0.005

        y_param = self.ylabel.text()
        y_min = float(self.yedit_min.text())
        y_max = float(self.yedit_max.text())
        self.parameter_iterator.set_axis_steps('y', self.network.NeuronGroups[1], y_param, y_min, y_max, self.ysteps, False)#'exponent', 3, 6

        print('refresh...')

        self.result_images=[]
        for x in range(self.xsteps*2):
            self.result_images.append([])
            for y in range(self.ysteps*2):
                self.result_images[-1].append([])

        self.parameter_iterator.start()

    def on_img_click(self, event):
        x = event.pos().x()
        y = event.pos().y()
        xp = int(self.xsteps*2 / self.content_qlabel.width() * x)
        yp = int(self.ysteps*2 - self.ysteps*2 / self.content_qlabel.height() * y)


        if hasattr(self, 'result_images') and xp>=0 and yp>=0 and len(self.result_images)>xp and len(self.result_images[xp])>yp:
            if len(self.result_images[xp][yp])>0:
                self.draw_qimage(self.result_images[xp][yp][0], 0, 0, self.detail_pixmap.width(), self.detail_pixmap.height(), pixmap=self.detail_pixmap)

        self.refresh_img()


    def draw_weights(self, xmax, ymax, xstep, ystep):
        x, y, step_img_width, step_img_height = self.get_x_y_w_h(xmax, ymax, xstep, ystep)
        data = get_whole_Network_weight_image(self.network.NeuronGroups[1], neuron_src_groups=None) * 255

        #plt.matshow(data)
        #plt.show()

        qimg = self.numpy_array_to_qimage(data)

        self.result_images[xstep][ystep].append(qimg)

        self.draw_qimage(qimg, x, y, step_img_width, step_img_height)

        self.refresh_img()


    def draw_pyplot(self, function, xmax, ymax, xstep, ystep, xlim=None, ylim=None):
        x, y, step_img_width, step_img_height = self.get_x_y_w_h(xmax, ymax, xstep, ystep)

        data = self.get_plot_mat(function, xlim, ylim)
        qimg = self.numpy_array_to_qimage(data, 4)
        self.result_images[xstep][ystep].append(qimg)

        self.draw_qimage(qimg, x, y, step_img_width, step_img_height)

        self.refresh_img()


    def get_x_y_w_h(self,xmax, ymax, xstep, ystep):
        step_img_width = (self.content_pixmap.width()-20)/xmax-1
        step_img_height = (self.content_pixmap.height()-20)/ymax-1
        x = 10+xstep*step_img_width
        y = 10+(ymax-ystep-1)*step_img_height
        return x, y, step_img_width, step_img_height


    def refresh_img(self):
        self.refresh_content_image()
        self.refresh_detail_image()

        #self.detail_qlabel.setPixmap(self.detail_pixmap)
        #self.detail_qlabel.repaint()

        #self.content_qlabel.setPixmap(self.content_pixmap)
        #self.content_qlabel.repaint()
        QtCore.QCoreApplication.processEvents()

    def get_plot_mat(self, function, xlim=None, ylim=None):
        fig = Figure(figsize=(5, 4), dpi=50)
        canvas = FigureCanvasAgg(fig)
        ax = fig.add_subplot(111)

        function(ax)

        ax.set_xlim(0)
        ax.set_ylim(0)

        if xlim is not None:
            ax.set_xlim(0, xlim)
        if ylim is not None:
            ax.set_ylim(0, ylim)

        canvas.draw()
        s, (width, height) = canvas.print_to_buffer()
        return np.fromstring(s, np.uint8).reshape((height, width, 4))























'''

class QTUI_New(QWidget):
    countChanged = pyqtSignal(int)
    cc = 0

    def __init__(self, network, param_list, label="Network_Test"):
        super().__init__()
        self.network = network

        self.parameter_iterator = Parameter_iterator(self.On_PI_Iteration)

        if param_list is None:
            self.param_list=[]
            d = network.group_value_dicts[self.network.NeuronGroups[1]]
            for key in d:
                if not type(d[key]) == list and not type(d[key]) == dict and not key in ['learning', 'activity', 'avg_act', 'glu_inter_gamma_activity', 'GABA_inter_gamma_activity', 'height', 'depth', 'width', 'size', 'GLU_density', 'GABA_density', 'GLU_strength', 'GABA_strength', 'x', 'y', 'z']:
                    self.param_list.append(key)

            #for id in self.network.NeuronGroups[1].behaviours:
            #    for dict_self.network.NeuronGroups[1].behaviours[id].__dict__


            self.param_list.sort()
        else:
            self.param_list = param_list

        self.init_QT_Window(label)
        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)
        self.init_QT_Elements()
        self.closeeventtriggered = False


    def init_QT_Window(self, label):
        self.xsteps=10
        self.ysteps=6
        self.width = 1500
        self.height = 800
        self.sidebar_width = 300
        self.btn_height = 20
        self.setWindowTitle(label)
        self.setGeometry(10, 10, self.width, self.height)

    def next_line(self, number=1):
        for i in range(number):
            self.ypos += self.btn_height

    def add_param_block(self, param):
        self.label[param] = QLabel(self)
        self.label[param].setWordWrap(True)
        self.label[param].setText(param)
        self.label[param].move(1, self.ypos)
        self.label[param].resize(self.sidebar_width / 3, self.btn_height)

        value=self.network.NeuronGroups[1].get_modification_value(param)
        range_percentage=0.5

        self.edits[param] = QLineEdit(self)
        self.edits[param].setText('{}'.format(value))
        self.edits[param].move(self.sidebar_width / 3 * 1, self.ypos)
        self.edits[param].resize(self.sidebar_width / 3, self.btn_height)

        def xset(event):
            self.xlabel.setText(param)
            self.xedit_min.setText('{}'.format(value*range_percentage))
            self.xedit_max.setText('{}'.format(value*(1+range_percentage)))

        def yset(event):
            self.ylabel.setText(param)
            self.yedit_min.setText('{}'.format(value*range_percentage))
            self.yedit_max.setText('{}'.format(value*(1+range_percentage)))

        self.btn[param] = QPushButton('x', self)
        self.btn[param].move(self.sidebar_width / 6 * 4, self.ypos)
        self.btn[param].resize(self.sidebar_width / 6, self.btn_height)
        self.btn[param].clicked.connect(xset)

        self.btn[param] = QPushButton('y', self)
        self.btn[param].move(self.sidebar_width / 6 * 5, self.ypos)
        self.btn[param].resize(self.sidebar_width / 6, self.btn_height)
        self.btn[param].clicked.connect(yset)

        self.next_line()



    def init_QT_Elements(self):

        self.detail_pixmap = QPixmap(self.sidebar_width, self.sidebar_width)
        self.detail_qlabel = QLabel(self)

        self.on_detail_click(None)

        self.detail_qlabel.setPixmap(self.detail_pixmap)
        self.detail_qlabel.move(0, 0)
        self.detail_qlabel.resize(self.sidebar_width, self.sidebar_width)
        self.detail_qlabel.mousePressEvent = self.on_detail_click

        self.ypos = self.sidebar_width


        self.label = {}
        self.edits = {}
        self.btn = {}
        for param in self.param_list:
            self.add_param_block(param)

        self.next_line(2)



        self.xlabel = QLabel(self)
        self.xlabel.setWordWrap(True)
        self.xlabel.setText("x")
        self.xlabel.move(1, self.ypos)
        self.xlabel.resize(self.sidebar_width, self.btn_height)
        self.next_line()

        self.xedit_min = QLineEdit(self)
        self.xedit_min.setText('')
        self.xedit_min.move(0, self.ypos)
        self.xedit_min.resize(self.sidebar_width / 2, self.btn_height)

        self.xedit_max = QLineEdit(self)
        self.xedit_max.setText('')
        self.xedit_max.move(self.sidebar_width / 2, self.ypos)
        self.xedit_max.resize(self.sidebar_width / 2, self.btn_height)
        self.next_line()


        self.ylabel = QLabel(self)
        self.ylabel.setWordWrap(True)
        self.ylabel.setText('y')
        self.ylabel.move(1, self.ypos)
        self.ylabel.resize(self.sidebar_width, self.btn_height)
        self.next_line()

        self.yedit_min = QLineEdit(self)
        self.yedit_min.setText('')
        self.yedit_min.move(0, self.ypos)
        self.yedit_min.resize(self.sidebar_width / 2, self.btn_height)

        self.yedit_max = QLineEdit(self)
        self.yedit_max.setText('')
        self.yedit_max.move(self.sidebar_width / 2, self.ypos)
        self.yedit_max.resize(self.sidebar_width / 2, self.btn_height)
        self.next_line(4)



        block_add_btn = QPushButton('refresh', self)
        block_add_btn.move(0, self.ypos)
        block_add_btn.resize(self.sidebar_width, self.btn_height)
        block_add_btn.clicked.connect(self.refresh_click)
        self.next_line()


        self.content_pixmap = QPixmap(self.width - self.sidebar_width, self.height)
        self.qlabel = QLabel(self)
        self.qlabel.setPixmap(self.content_pixmap)
        self.qlabel.move(self.sidebar_width, 0)
        self.qlabel.resize(self.width-self.sidebar_width, self.height)


        self.qlabel.mousePressEvent = self.on_img_click


        self.show()

    def on_detail_click(self, event):
        qimg = self.numpy_array_to_qimage(get_reconstruction_activations(self.network.NeuronGroups[0][TRENNeuronActivator].get_pattern_samples(50), 10, 10)*255, byte_count=1)
        self.draw_numpy_array(qimg, 0, 0, self.sidebar_width, self.sidebar_width, pixmap=self.detail_pixmap)
        if event is not None:
            self.refresh_img()


    def on_img_click(self, event):
        x = event.pos().x()
        y = event.pos().y()
        xp = int(self.xsteps*2 / self.content_pixmap.width() * x)
        yp = int(self.ysteps*2 - self.ysteps*2 / self.content_pixmap.height() * y)

        print(xp, yp)

        if hasattr(self, 'result_images') and xp>=0 and yp>=0 and len(self.result_images)>xp and len(self.result_images[xp])>yp:
            self.draw_numpy_array(self.result_images[xp][yp][0], 0, 0, self.sidebar_width, self.sidebar_width, pixmap=self.detail_pixmap)

        self.refresh_img()


    def On_PI_Iteration(self, axis):
        self.network.reset()

        for param in self.param_list:
            self.network.NeuronGroups[1].set_modification_value(param, float(self.edits[param].text()))


        self.network.NeuronGroups[1].set_modification_value(axis['x'].target_attribute_name, axis['x'].current_value)
        self.network.NeuronGroups[1].set_modification_value(axis['y'].target_attribute_name, axis['y'].current_value)

        print(axis['x'].target_attribute_name, axis['x'].current_value)
        print(axis['y'].target_attribute_name, axis['y'].current_value)

        for i in range(10000):
            self.network.simulate_iteration()
            #if i%500==0:

        xmax=len(axis['x'].values)*2
        ymax=len(axis['y'].values)*2
        xstep=axis['x'].step*2
        ystep=axis['y'].step*2

        self.draw_weights(xmax, ymax, xstep, ystep)

        def act_hist_plt(ax): ax.hist(np.array(self.network.NeuronGroups[1][TRENRecorder].activity)[:, 0], bins=20)
        self.draw_pyplot(act_hist_plt, xmax, ymax, xstep+1, ystep,xlim=1)

        def reward_hist_plt(ax): ax.hist(np.array(self.network.NeuronGroups[1][TRENRecorder].reward)[:, 0], bins=20)
        self.draw_pyplot(reward_hist_plt, xmax, ymax, xstep+1, ystep+1,xlim=1)

        def norm_plt(ax): ax.plot(np.array(self.network.NeuronGroups[1][TRENRecorder].norm_value)[:, 0])
        self.draw_pyplot(norm_plt, xmax, ymax, xstep, ystep+1)





    def get_x_y_w_h(self,xmax, ymax, xstep, ystep):
        step_img_width = (self.content_pixmap.width()-20)/xmax-1
        step_img_height = (self.content_pixmap.height()-20)/ymax-1
        x = 10+xstep*step_img_width
        y = 10+(ymax-ystep-1)*step_img_height
        return x, y, step_img_width, step_img_height

    def refresh_img(self):
        self.detail_qlabel.setPixmap(self.detail_pixmap)
        self.detail_qlabel.repaint()

        self.detail_qlabel.setPixmap(self.content_pixmap)
        self.qlabel.repaint()
        QtCore.QCoreApplication.processEvents()

    def get_plot_mat(self, function, xlim=None, ylim=None):
        fig = Figure(figsize=(5, 4), dpi=50)
        canvas = FigureCanvasAgg(fig)
        ax = fig.add_subplot(111)

        function(ax)

        ax.set_xlim(0)
        ax.set_ylim(0)

        if xlim is not None:
            ax.set_xlim(0, xlim)
        if ylim is not None:
            ax.set_ylim(0, ylim)

        canvas.draw()
        s, (width, height) = canvas.print_to_buffer()
        return np.fromstring(s, np.uint8).reshape((height, width, 4))


    def draw_pyplot(self, function, xmax, ymax, xstep, ystep, xlim=None, ylim=None):
        x, y, step_img_width, step_img_height = self.get_x_y_w_h(xmax, ymax, xstep, ystep)

        data = self.get_plot_mat(function, xlim, ylim)
        qimg = self.numpy_array_to_qimage(data, 4)
        self.result_images[xstep][ystep].append(qimg)

        self.draw_numpy_array(qimg, x, y, step_img_width, step_img_height)

        self.refresh_img()



    def draw_weights(self, xmax, ymax, xstep, ystep):

        x, y, step_img_width, step_img_height = self.get_x_y_w_h(xmax, ymax, xstep, ystep)

        data = get_whole_Network_weight_image(self.network.NeuronGroups[1], neuron_src_groups=None) * 255

        qimg = self.numpy_array_to_qimage(data)

        self.result_images[xstep][ystep].append(qimg)

        self.draw_numpy_array(qimg, x, y, step_img_width, step_img_height)

        self.refresh_img()



    def refresh_click(self, event):


        x_param=self.xlabel.text()
        x_min=float(self.xedit_min.text())
        x_max=float(self.xedit_max.text())
        self.parameter_iterator.set_axis_steps('x', self.network.NeuronGroups[1], x_param, x_min, x_max, self.xsteps, False)#'post_learn_value', 0.0005, 0.005

        y_param=self.ylabel.text()
        y_min=float(self.yedit_min.text())
        y_max=float(self.yedit_max.text())
        self.parameter_iterator.set_axis_steps('y', self.network.NeuronGroups[1], y_param, y_min, y_max, self.ysteps, False)#'exponent', 3, 6

        print('refresh...')

        self.result_images=[]
        for x in range(self.xsteps*2):
            self.result_images.append([])
            for y in range(self.ysteps*2):
                self.result_images[-1].append([])

        self.parameter_iterator.start()



    def draw_numpy_array(self, qimg, x, y, w, h, pixmap=None):
        if pixmap is None:
            pixmap=self.content_pixmap
        painter = QPainter(pixmap)
        painter.drawImage(QtCore.QRect(x, y, w, h), qimg, QtCore.QRect(0, 0, qimg.width(), qimg.height()))


    def numpy_array_to_qimage(self, data, byte_count=3, alpha=255):
        data = data.astype(int)
        bytesPerLine = byte_count * data.shape[1]

        if byte_count == 1: format = QImage.Format_Grayscale8
        if byte_count == 3: format = QImage.Format_RGB888
        if byte_count == 4: format = QImage.Format_RGBA8888

        if byte_count == 4 and alpha < 255:
            data[:, :, 3] = alpha

        return QImage(np.require(data, np.uint8, 'C'), data.shape[1], data.shape[0], bytesPerLine, format)


def start_TREN_UI(network, paramlist):
    app = QApplication(sys.argv)
    ui = QTUI_New(network, paramlist, "TREN2")
    sys.exit(app.exec_())



'''