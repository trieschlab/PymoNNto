#import matplotlib
#matplotlib.use('Qt5Agg')

from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np
#from Exploration.Visualization.Visualization_Helper import *

import sys

sys._excepthook = sys.excepthook
def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
#    sys._excepthook(exctype, value, traceback)
    sys.exit(1)
sys.excepthook = exception_hook

class UI_Base(QApplication):

    def __init__(self, network, label="Network_Test"):
        super().__init__(sys.argv)

        self.network = network

        self.main_window = QWidget()

        self.init_QT_Window(label)
        quit = QAction("Quit", self.main_window)
        quit.triggered.connect(self.main_window.closeEvent)
        self.closeeventtriggered = False

    def show(self):
        self.main_window.show()
        sys.exit(self.exec_())

    def Add_element(self, elem, sidebar=False, stretch=1):
        if sidebar:
            self.Add_Sidebar_Element(elem)
        else:
            self.current_H_block.addWidget(elem, stretch=stretch)

    def Add_plot(self, title=None, sidebar=False, stretch=1, axisItems=None, x_label=None, y_label=None, always_show_axis_labels=False, tooltip_message=None):
        canvas = pg.GraphicsLayoutWidget()
        canvas.setBackground((255, 255, 255))

        if tooltip_message is not None:
            canvas.ci.setToolTip(tooltip_message)

        self.Add_element(canvas, sidebar, stretch)

        plt = canvas.addPlot(row=0, col=0, axisItems=axisItems)

        if always_show_axis_labels or not self.reduced_layout:
            if x_label is not None:
                plt.getAxis('bottom').setLabel(text=x_label)
            if y_label is not None:
                plt.getAxis('left').setLabel(text=y_label)

        if title is not None:
            plt.setLabels(title=title)
        return plt

    def Add_Image_Item(self, return_plot=False, sidebar=False, stretch=1, title=None, tooltip_message=None):
        canvas = pg.GraphicsLayoutWidget()

        if tooltip_message is not None:
            canvas.ci.setToolTip(tooltip_message)

        #canvas.ci.layout.setContentsMargins(0, 0, 0, 0)
        #canvas.ci.layout.setSpacing(0)

        canvas.setBackground((255, 255, 255))

        self.Add_element(canvas, sidebar, stretch)

        plot = canvas.addPlot(row=0, col=0)
        #plot.setContentsMargins(0,0,0,0)

        if title is not None:
            plot.setLabels(title=title)

        plot.hideAxis('left')
        plot.hideAxis('bottom')
        image_item = pg.ImageItem(np.random.rand(291, 291, 3))

        plot.addItem(image_item)
        if return_plot:
            return image_item, plot
        else:
            return image_item


    def Add_plot_curve(self, title=None, return_plot=False, sidebar=False, stretch=1, number_of_curves=1, colors=[(0, 0, 0),(255, 0, 0),(0, 0, 255),(0, 250, 150),(255, 0, 255)], lines=[], names=[''], legend=False, x_label=None, y_label=None, return_list=False, always_show_axis_labels=False, tooltip_message=None):
        plt = self.Add_plot(title, sidebar, stretch, tooltip_message=tooltip_message)

        if always_show_axis_labels or not self.reduced_layout:
            if x_label is not None:
                plt.getAxis('bottom').setLabel(text=x_label)
            if y_label is not None:
                plt.getAxis('left').setLabel(text=y_label)

        if legend:
            plt.addLegend()

        for line in lines:
            plt.addLine(y=line)

        curves=[]
        for i in range(number_of_curves):
            curve = pg.PlotCurveItem([], name=names[i%len(names)], pen=colors[i%len(colors)])

            plt.addItem(curve)
            curves.append(curve)
        if number_of_curves == 1 and not return_list:
            curves = curves[0]




        if return_plot:
            return curves, plt
        else:
            return curves

    def Next_Tab(self, title='', stretch=1):

        main_tab_container = QWidget()

        #def to_window(event):
        #    indx=self.tabs.indexOf(main_tab_container)
        #    self.tabs.removeTab(indx)
        #    main_tab_container.setParent(None)
        #    main_tab_container.show()

        def to_tab(event):
            self.tabs.addTab(main_tab_container, title)

        #main_tab_container.mousePressEvent = to_window
        main_tab_container.closeEvent = to_tab
        main_tab_container.setWindowTitle(title)

        #bl = QHBoxLayout(self.main_tab_container)
        #bl.addWidget(self.net_info_text_label)
        self.tabs.addTab(main_tab_container, title)
        self.visualization_layout = QVBoxLayout(main_tab_container)
        self.Next_H_Block(stretch)
        return main_tab_container


    def Next_H_Block(self,stretch=1):
        self.current_H_block = QHBoxLayout()
        self.visualization_layout.addLayout(self.current_H_block, stretch=stretch)

    def init_QT_Window(self, label):
        self.width = 1200
        self.height = 600
        self.main_window.setWindowTitle(label)
        self.main_window.setGeometry(10, 40, self.width, self.height)


        self.main_h_layout = QHBoxLayout(self.main_window)

        self.sidebar_column_layout = QHBoxLayout()
        self.main_h_layout.addLayout(self.sidebar_column_layout, stretch=2)

        self.Add_New_Sidebar_Column()

        cont=QVBoxLayout()

        self.tabs = QTabWidget()
        cont.addWidget(self.tabs)
        self.main_h_layout.addLayout(cont, stretch=8)


        #self.main_tab_container = QWidget()
        #self.visualization_layout = QVBoxLayout(self.main_tab_container)
        #self.tabs.addTab(self.main_tab_container, "Main")

        #self.Next_Tab('Main')


    def create_detail_label_pixmap(self):
        self.detail_qlabel = QLabel()
        self.detail_qlabel.setScaledContents(True)
        self.Add_Sidebar_Element(self.detail_qlabel,stretch=10)
        self.update_detail_image()

    def update_detail_image(self):
        self.detail_pixmap = QPixmap(self.detail_qlabel.width(), self.detail_qlabel.height())
        painter = QPainter(self.detail_pixmap)
        painter.eraseRect(0, 0, self.detail_qlabel.width(), self.detail_qlabel.height())
        self.refresh_detail_image()

    def refresh_detail_image(self):
        self.detail_qlabel.setPixmap(self.detail_pixmap)
        self.detail_qlabel.repaint()



    def create_content_label_pixmap(self):
        self.content_qlabel = QLabel()
        self.content_qlabel.setScaledContents(True)
        self.visualization_layout.addWidget(self.content_qlabel, stretch=1)
        self.update_content_image()

    def update_content_image(self):
        self.content_pixmap = QPixmap(self.content_qlabel.width(), self.content_qlabel.height())
        painter = QPainter(self.content_pixmap)
        painter.eraseRect(0, 0, self.content_qlabel.width(), self.content_qlabel.height())
        self.refresh_content_image()

    def refresh_content_image(self):
        self.content_qlabel.setPixmap(self.content_pixmap)
        self.content_qlabel.repaint()




    def Add_New_Sidebar_Column(self):
        self.sidebar_current_vertical_layout = QVBoxLayout()
        #self.sidebar_current_vertical_layout.setSpacing(0)
        #self.sidebar_current_vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_column_layout.addLayout(self.sidebar_current_vertical_layout, stretch=1)

    def Add_Sidebar_Spacing(self):
        self.Add_Sidebar_Element(QLabel())

    def Add_Sidebar_Element(self, elements=[], percentages=None, stretch=1, return_h_layout=False):
        if type(elements) is not list: elements=[elements]
        if percentages is None: percentages=[1 for _ in elements]

        self.sidebar_hblock = QHBoxLayout()
        #block.setSpacing(0)
        #block.setMargin(0)
        #block.setContentsMargins(0, 0, 0, 0)

        for element,p in zip(elements,percentages):
            self.sidebar_hblock.addWidget(element,stretch=p)

        self.sidebar_current_vertical_layout.addLayout(self.sidebar_hblock, stretch=stretch)
        if return_h_layout:
            return self.sidebar_hblock
        else:
            return elements




    def draw_qimage(self, qimg, x, y, w, h, pixmap=None):
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


#tqt = TREN_QT_UI_Base(None)
#tqt.show()

#########################
#########################Manual
#########################

'''
self.create_detail_label_pixmap()
self.create_content_label_pixmap()

for i in range(5):
    self.Add_Sidebar_Element([QPushButton('refresh', self.main_window), QPushButton('refresh', self.main_window)])


def onclick(event):
    self.update_detail_image()
    self.update_content_image()

    painter = QPainter(self.detail_pixmap)
    pen = QPen(QColor(255, 255, 0), 3)
    painter.setPen(pen)
    painter.drawLine(10, 10, 100, 100)
    painter.drawRect(painter.clipBoundingRect())

    self.refresh_content_image()
    self.refresh_detail_image()

    # print('adssgdf')


for i in range(5):
    self.Add_Sidebar_Element(QPushButton('refresh', self.main_window))[0].clicked.connect(onclick)

self.Add_Sidebar_Spacing()

self.Add_New_Sidebar_Column()

self.Add_Sidebar_Spacing()

for i in range(5):
    self.Add_Sidebar_Element(QPushButton('refresh', self.main_window))
'''

