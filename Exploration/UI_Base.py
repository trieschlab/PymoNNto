#import matplotlib
#matplotlib.use('Qt5Agg')

from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np
#from Exploration.Visualization.Visualization_Helper import *

from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtCore import Qt, QPoint, QMimeData
from PyQt5.QtGui import QPixmap, QRegion, QDrag, QCursor

import sys
import PymoNNto

from functools import wraps
from pyqtgraph.graphicsItems.PlotItem import PlotItem

sys._excepthook = sys.excepthook

def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
#    sys._excepthook(exctype, value, traceback)
    sys.exit(1)
sys.excepthook = exception_hook

def deprecated_warning(message):
    def inner_function(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            #raise Exception(message)
            print(message)
            return function(*args, **kwargs)
        return wrapper
    return inner_function


default_colors=[(0, 0, 0),(255, 0, 0),(0, 0, 255),(0, 250, 150),(255, 0, 255)]

class UI_Base(QApplication):

    def __init__(self, title="Network_Test", create_sidebar=True, create_tab_grid=True):#network
        super().__init__(sys.argv)

        path = PymoNNto.__file__.replace('__init__.py', '')+ 'icon3232.png'

        if 'win' in sys.platform and sys.platform != 'darwin':
            import ctypes
            myappid = 'mv.Pymonnto.ui.1'  # arbitrary string mycompany.myproduct.subproduct.version
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        self._set_icon(path)

        self.reduced_layout = False

        self.main_window = QWidget()
        self.main_window.keyPressEvent = self.keyPressEvent
        self.main_window.keyReleaseEvent = self.keyReleaseEvent
        self.control_key_down=False

        self.init_QT_Window(title, create_sidebar, create_tab_grid)
        quit = QAction("Quit", self.main_window)
        quit.triggered.connect(self.main_window.closeEvent)
        self.closeeventtriggered = False

    def _set_icon(self, path):
        app_icon = QIcon()
        app_icon.addFile(path, QtCore.QSize(32, 32))
        self.setWindowIcon(app_icon)

    def show(self):
        self.main_window.show()
        sys.exit(self.exec_())

    def init_QT_Window(self, label, create_sidebar=True, create_tab_grid=True):
        self.width = 1200
        self.height = 600
        self.main_window.setWindowTitle(label)
        self.main_window.setGeometry(10, 40, self.width, self.height)

        self.main_h_layout = QHBoxLayout(self.main_window)

        self.main_split = QSplitter()
        self.main_h_layout.addWidget(self.main_split)

        if create_sidebar:
            self.sidebar = QRow_Column_Widget(self)
            self.main_split.addWidget(self.sidebar)

        self.add_tab_grid(create_tab_grid=create_tab_grid)


    def remove_tab(self, tab):
        for tab_widget in self._tab_widgets:
            indx = tab_widget.indexOf(tab)
            if indx!=-1:
                tab_widget.removeTab(indx)

    def add_tab_grid(self, create_tab_grid=True):

        self.tabs = MyTabWidget(new=True)
        self._tab_widgets = [self.tabs]

        if not create_tab_grid:
            self.main_split.addWidget(self.tabs)
        else:
            self.vsplit = QSplitter()
            self.vsplit.setOrientation(Qt.Vertical)
            #...
            self.hsplit1 = QSplitter()

            self.tabs2 = MyTabWidget(new=True)
            self._tab_widgets.append(self.tabs2)
            self.hsplit1.addWidget(self.tabs)
            self.hsplit1.addWidget(self.tabs2)
            self.hsplit1.setSizes([1, 0])

            self.hsplit2 = QSplitter()
            self.tabs3 = MyTabWidget(new=True)
            self._tab_widgets.append(self.tabs3)
            self.tabs4 = MyTabWidget(new=True)
            self._tab_widgets.append(self.tabs4)
            self.hsplit2.addWidget(self.tabs3)
            self.hsplit2.addWidget(self.tabs4)
            self.hsplit2.setSizes([1, 0])

            self.vsplit.addWidget(self.hsplit1)
            self.vsplit.addWidget(self.hsplit2)
            self.vsplit.setSizes([1, 0])

            self.main_split.addWidget(self.vsplit)
            self.main_split.setSizes([300, 800])

            self.tabs.currentChanged.connect(self._onTabChange)
            self.tabs2.currentChanged.connect(self._onTabChange)
            self.tabs3.currentChanged.connect(self._onTabChange)
            self.tabs4.currentChanged.connect(self._onTabChange)

    def _onTabChange(self, i):
        self.on_tab_change(i)

    def on_tab_change(self, i):
        return #overwrite

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.control_key_down=False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.control_key_down=True

        if event.key() in [Qt.Key_N, Qt.Key_C, Qt.Key_T, Qt.Key_M]:
            self.text_input_dialog('Please enter Note:', 'set note', self.set_note, default_text='-')

        if event.key() == Qt.Key_W:
            indx = self.tabs.currentIndex()
            if indx >= 0:
                widget=self.tabs.currentWidget()
                self.tabs.removeTab(indx)
                widget.setParent(None)
                widget.setWindowTitle('Warning: experimental feature (closing/reattaching the window can lead to crashes)')
                widget.show()

        if event.key() == Qt.Key_Space:
            self.pause = not self.pause

        if event.key() == Qt.Key_1:
            self.vsplit.setSizes([100000, 0])
            self.hsplit1.setSizes([100000, 0])
            self.hsplit2.setSizes([100000, 0])

        if event.key() == Qt.Key_2:
            self.vsplit.setSizes([100000, 100000])
            self.hsplit1.setSizes([100000, 0])
            self.hsplit2.setSizes([100000, 0])

        if event.key() == Qt.Key_3:
            self.vsplit.setSizes([100000, 100000])
            self.hsplit1.setSizes([100000, 100000])
            self.hsplit2.setSizes([100000, 0])

        if event.key() == Qt.Key_4:
            self.vsplit.setSizes([100000, 100000])
            self.hsplit1.setSizes([100000, 100000])
            self.hsplit2.setSizes([100000, 100000])

        if event.key() == Qt.Key_5:
            self.vsplit.setSizes([100000, 100000])
            self.hsplit1.setSizes([100000, 0])
            self.hsplit2.setSizes([100000, 100000])

        if event.key() == Qt.Key_6:
            self.vsplit.setSizes([100000, 100000])
            self.hsplit1.setSizes([100000, 100000])
            self.hsplit2.setSizes([100000, 0])

        if event.key() == Qt.Key_7:
            self.vsplit.setSizes([100000, 0])
            self.hsplit1.setSizes([100000, 100000])
            self.hsplit2.setSizes([100000, 0])

    def set_note(self, note_str):
        self.main_window.setWindowTitle(self.main_window.windowTitle() + ' | ' + note_str)
        if note_str=='-':
            self.main_window.setWindowTitle(self.main_window.windowTitle().split('|')[0])

    def text_input_dialog(self, txt, btn_text, func, default_text=''):
        dlg = QDialog()
        dlg.setWindowTitle(txt)
        layout = QVBoxLayout()

        input_le = QLineEdit(default_text)
        layout.addWidget(input_le)

        def btn_clicked():
            func(input_le.text())
            dlg.close()

        btn = QPushButton(btn_text)
        btn.clicked.connect(btn_clicked)

        layout.addWidget(btn)
        dlg.setLayout(layout)
        dlg.resize(300, 50)
        dlg.exec()

    def show_message(self, title, message, btn_text='Ok'):
        dlg = QDialog()
        dlg.setWindowTitle(title)
        layout = QVBoxLayout()

        label = QLabel(message)
        layout.addWidget(label)

        def btn_clicked():
            dlg.close()

        btn = QPushButton(btn_text)
        btn.clicked.connect(btn_clicked)

        layout.addWidget(btn)
        dlg.setLayout(layout)
        dlg.resize(300, 50)
        dlg.exec()





    def add_tab(self, title='', stretch=100):
        self.tab = QRow_Column_Widget(self)

        def to_tab(event):
            self.tabs.addTab(self.tab, title)

        self.tab.closeEvent = to_tab
        self.tab.setWindowTitle(title)
        self.tabs.addTab(self.tab, title)
        #self.tab_current_layout = QVBoxLayout(main_tab_container)
        self.tab.add_row(stretch=stretch)
        return self.tab






    ################################################################################################
    #deprecated#####################################################################################
    ################################################################################################

    @deprecated_warning("Add_element function will be removed in coming versions. Please use tab/sidebar.add_widget instead.")
    def Add_element(self, elem, sidebar=False, stretch=1):
        return self.tab.add_widget(elem, sidebar=sidebar, stretch=stretch)
        #if sidebar:
        #    self.Add_Sidebar_Element(elem, stretch=stretch)#new stretch
        #else:
        #    self.current_H_block.addWidget(elem, stretch=stretch)
        #return elem

    @deprecated_warning("Add_plot function will be removed in coming versions. Please use tab/sidebar.add_plot instead.")
    def Add_plot(self, title=None, stretch=1, axisItems=None, x_label=None, y_label=None, always_show_axis_labels=False, tooltip_message=None):
        return self.tab.add_plot(title=title, stretch=stretch, axisItems=axisItems, x_label=x_label, y_label=y_label, tooltip_message=tooltip_message)
        #canvas = pg.GraphicsLayoutWidget()
        #canvas.setBackground((255, 255, 255))

        #if tooltip_message is not None:
        #    canvas.ci.setToolTip(tooltip_message)

        #self.Add_element(canvas, sidebar, stretch)

        #plt = canvas.addPlot(row=0, col=0, axisItems=axisItems)

        #if always_show_axis_labels or not self.reduced_layout:
        #    if x_label is not None:
        #        plt.getAxis('bottom').setLabel(text=x_label)
        #    if y_label is not None:
        #        plt.getAxis('left').setLabel(text=y_label)

        #if title is not None:
        #    plt.setLabels(title=title)
        #return plt

    @deprecated_warning("Add_Image_Item function will be removed in coming versions. Please use tab/sidebar.add_plot().add_image instead.")
    def Add_Image_Item(self, return_plot=False, sidebar=False, stretch=1, title=None, tooltip_message=None):
        plot = self.tab.add_plot(title=title, stretch=stretch, tooltip_message=tooltip_message)
        image_item = plot.add_image()

        #canvas = pg.GraphicsLayoutWidget()

        #if tooltip_message is not None:
        #    canvas.ci.setToolTip(tooltip_message)

        ##canvas.ci.layout.setContentsMargins(0, 0, 0, 0)
        ##canvas.ci.layout.setSpacing(0)

        #canvas.setBackground((255, 255, 255))

        #self.Add_element(canvas, sidebar, stretch)

        #plot = canvas.addPlot(row=0, col=0)
        ##plot.setContentsMargins(0,0,0,0)

        #if title is not None:
        #    plot.setLabels(title=title)

        #plot.hideAxis('left')
        #plot.hideAxis('bottom')
        #image_item = pg.ImageItem(np.random.rand(291, 291, 3))

        #plot.addItem(image_item)
        if return_plot:
            return image_item, plot
        else:
            return image_item

    @deprecated_warning("Add_plot_curve function will be removed in coming versions. Please use tab/sidebar.add_plot().add_curves instead.")
    def Add_plot_curve(self, title=None, return_plot=False, sidebar=False, stretch=1, number_of_curves=1, colors=[(0, 0, 0),(255, 0, 0),(0, 0, 255),(0, 250, 150),(255, 0, 255)], lines=[], names=[''], legend=False, x_label=None, y_label=None, return_list=False, always_show_axis_labels=False, tooltip_message=None):
        plot = self.tab.add_plot(title=title, stretch=stretch, x_label=x_label, y_label=y_label, tooltip_message=tooltip_message)
        curves = plot.add_curves(number_of_curves=number_of_curves, colors=colors, lines=lines, names=names, legend=legend)

        #plt = self.Add_plot(title, sidebar, stretch, tooltip_message=tooltip_message)

        #if always_show_axis_labels or not self.reduced_layout:
        #    if x_label is not None:
        #        plt.getAxis('bottom').setLabel(text=x_label)
        #    if y_label is not None:
        #        plt.getAxis('left').setLabel(text=y_label)

        #if legend:
        #    plt.addLegend()

        #for line in lines:
        #    plt.addLine(y=line,pen=(50,50,50,255))

        #curves=[]
        #for i in range(number_of_curves):
        #    curve = pg.PlotCurveItem([], name=names[i%len(names)], pen=colors[i%len(colors)])

        #    plt.addItem(curve)
        #    curves.append(curve)
        #if number_of_curves == 1 and not return_list:
        #    curves = curves[0]

        if return_plot:
            return curves, plot
        else:
            return curves

    @deprecated_warning("Next_Tab function will be removed in coming versions. Please use add_tab instead.")
    def Next_Tab(self, title='', stretch=100 , create_h_block=True):
        return self.add_tab(title=title, stretch=stretch)#, create_h_block=create_h_block
        #main_tab_container = QWidget()

        #def to_tab(event):
        #    self.tabs.addTab(main_tab_container, title)

        #main_tab_container.closeEvent = to_tab
        #main_tab_container.setWindowTitle(title)

        ##bl = QHBoxLayout(self.main_tab_container)
        ##bl.addWidget(self.net_info_text_label)
        #self.tabs.addTab(main_tab_container, title)
        #self.visualization_layout = QVBoxLayout(main_tab_container)
        #if create_h_block:
        #    self.Next_H_Block(stretch)
        #return main_tab_container

    @deprecated_warning("Next_H_Block function will be removed in coming versions. Please use tab/sidebar.add_row instead.")
    def Next_H_Block(self,stretch=100):
        return self.tab.add_row(stretch=stretch)
        #self.current_H_block = QHBoxLayout()
        #self.visualization_layout.addLayout(self.current_H_block, stretch=stretch)

    #@deprecated_warning("Add_New_Sidebar_Column function will be removed in coming versions.")
    #def Add_New_Sidebar_Column(self):
    #    self.sidebar_current_vertical_layout = QVBoxLayout()
    #    #self.sidebar_current_vertical_layout.setSpacing(0)
    #    #self.sidebar_current_vertical_layout.setContentsMargins(0, 0, 0, 0)
    #    self.sidebar_column_layout.addLayout(self.sidebar_current_vertical_layout, stretch=1)

    @deprecated_warning("Add_Sidebar_Spacing function will be removed in coming versions. Please use sidebar.add_widget(QLabel()) instead.")
    def Add_Sidebar_Spacing(self):
        self.add_sidebar_widget(QLabel())
        #self.Add_Sidebar_Element(QLabel())

    @deprecated_warning("Add_Sidebar_Element function will be removed in coming versions. Please use sidebar.add_widget(..., sidebar=True)")
    def Add_Sidebar_Element(self, elements=[], percentages=None, stretch=100, return_h_layout=False):
        #self.add_sidebar_widget(elements)

        if type(elements) is not list: elements=[elements]
        if percentages is None: percentages=[1 for _ in elements]

        #self.sidebar_hblock = QHBoxLayout()
        ##block.setSpacing(0)
        ##block.setMargin(0)
        ##block.setContentsMargins(0, 0, 0, 0)

        layout = self.sidebar.add_column(stretch=stretch)

        for element,p in zip(elements,percentages):
            self.sidebar.add_widget(element, stretch=p)
            #self.sidebar_hblock.addWidget(element,stretch=p)

        self.sidebar.set_parent_layout()

        #self.sidebar_current_vertical_layout.addLayout(self.sidebar_hblock, stretch=stretch)
        if return_h_layout:
            return layout
        else:
            return elements



    #def create_detail_label_pixmap(self):
    #    self.detail_qlabel = QLabel()
    #    self.detail_qlabel.setScaledContents(True)
    #    self.Add_Sidebar_Element(self.detail_qlabel,stretch=10)
    #    self.update_detail_image()

    #def update_detail_image(self):
    #    self.detail_pixmap = QPixmap(self.detail_qlabel.width(), self.detail_qlabel.height())
    #    painter = QPainter(self.detail_pixmap)
    #    painter.eraseRect(0, 0, self.detail_qlabel.width(), self.detail_qlabel.height())
    #    self.refresh_detail_image()

    #def refresh_detail_image(self):
    #    self.detail_qlabel.setPixmap(self.detail_pixmap)
    #    self.detail_qlabel.repaint()



    #def create_content_label_pixmap(self):
    #    self.content_qlabel = QLabel()
    #    self.content_qlabel.setScaledContents(True)
    #    self.visualization_layout.addWidget(self.content_qlabel, stretch=1)
    #    self.update_content_image()

    #def update_content_image(self):
    #    self.content_pixmap = QPixmap(self.content_qlabel.width(), self.content_qlabel.height())
    #    painter = QPainter(self.content_pixmap)
    #    painter.eraseRect(0, 0, self.content_qlabel.width(), self.content_qlabel.height())
    #    self.refresh_content_image()

    #def refresh_content_image(self):
    #    self.content_qlabel.setPixmap(self.content_pixmap)
    #    self.content_qlabel.repaint()


    #def draw_qimage(self, qimg, x, y, w, h, pixmap=None):
    #    if pixmap is None:
    #        pixmap=self.content_pixmap
    #    painter = QPainter(pixmap)
    #    painter.drawImage(QtCore.QRect(x, y, w, h), qimg, QtCore.QRect(0, 0, qimg.width(), qimg.height()))


    #def numpy_array_to_qimage(self, data, byte_count=3, alpha=255):
    #    data = data.astype(int)
    #    bytesPerLine = byte_count * data.shape[1]

    #    if byte_count == 1: format = QImage.Format_Grayscale8
    #    if byte_count == 3: format = QImage.Format_RGB888
    #    if byte_count == 4: format = QImage.Format_RGBA8888

    #    if byte_count == 4 and alpha < 255:
    #        data[:, :, 3] = alpha

    #    return QImage(np.require(data, np.uint8, 'C'), data.shape[1], data.shape[0], bytesPerLine, format)


class QRow_Column_Widget(QWidget):

    def __init__(self, _parent):
        super().__init__()
        self._parent = _parent
        self.current_layout = QVBoxLayout()
        self.setLayout(self.current_layout)


    def add_widget(self, widget, stretch=100, sidebar=False):
        if type(widget) == list:
            for w in widget:
                self.get_layout().addWidget(w, stretch=stretch)
        else:
            self.get_layout().addWidget(widget, stretch=stretch)
        return widget

    def add_graphics_layout_widget(self, tooltip_message=None, stretch=100):
        graphics_layout_widget = pg.GraphicsLayoutWidget()
        graphics_layout_widget.setBackground((255, 255, 255))

        if tooltip_message is not None:
            graphics_layout_widget.ci.setToolTip(tooltip_message)

        self.add_widget(graphics_layout_widget, stretch=stretch)
        return graphics_layout_widget


    def add_plot(self, title=None, tooltip_message=None, axisItems=None, x_label=None, y_label=None, stretch=100):
        graphics_layout_widget = self.add_graphics_layout_widget(tooltip_message=tooltip_message, stretch=stretch)

        #plot = graphics_layout_widget.addPlot(row=0, col=0, axisItems=axisItems)
        plot = PymoNNto_PlotItem(axisItems=axisItems)
        graphics_layout_widget.addItem(plot, row=0, col=0)

        if not self._parent.reduced_layout:

            if x_label is not None:
                plot.getAxis('bottom').setLabel(text=x_label)

            if y_label is not None:
                plot.getAxis('left').setLabel(text=y_label)

        if title is not None:
            plot.setLabels(title=title)

        return plot

    def add_row(self, stretch=100, add_to_parent=True):
        if add_to_parent:
            self.set_parent_layout()
        layout = QHBoxLayout()
        layout._parent = self.get_layout()
        layout._parent.addLayout(layout, stretch=stretch)
        self.set_layout(layout)
        return layout

    def add_column(self, stretch=100, add_to_parent=True):
        if add_to_parent:
            self.set_parent_layout()
        layout = QVBoxLayout()
        layout._parent = self.get_layout()
        layout._parent.addLayout(layout, stretch=stretch)
        self.set_layout(layout)
        return layout

    def set_parent_layout(self, root=False):
        current = self.get_layout()
        if hasattr(current, '_parent') and current._parent is not None:
            self.set_layout(self.get_layout()._parent)
            if root:
                self.set_parent_layout(root=root)



    def get_layout(self):
            return self.current_layout

    def set_layout(self, layout):
        self.current_layout = layout




class PymoNNto_PlotItem(PlotItem):

    def add_curves(self, number_of_curves=1, colors=default_colors, lines=[], names=[''], legend=False, return_list=False):

        for line in lines:
            self.addLine(y=line, pen=(50, 50, 50, 255))

        curves = []
        for i in range(number_of_curves):
            curve = pg.PlotCurveItem([], name=names[i % len(names)], pen=colors[i % len(colors)])
            self.addItem(curve)
            curves.append(curve)

        #if number_of_curves == 1 and not return_list:
        #    curves = curves[0]

        if legend:
            self.addLegend()

        return curves

    def add_image(self):
        self.hideAxis('left')
        self.hideAxis('bottom')
        image_item = pg.ImageItem()#np.zeros((100, 100, 3))
        self.addItem(image_item)
        return image_item

    def add_text(self, txt):
        text_item = pg.TextItem(txt)
        self.addItem(text_item)
        return text_item


class MyTabWidget(QTabWidget):

   def __init__(self, parent=None, new=None):
      super().__init__(parent)
      self.setAcceptDrops(True)
      self.tabBar().setMouseTracking(True)
      self.setMovable(True)
      if new:
         MyTabWidget.setup(self)

   def __setstate__(self, data):
      self.__init__(new=False)
      self.setParent(data['parent'])
      for widget, tabname in data['tabs']:
         self.addTab(widget, tabname)
      MyTabWidget.setup(self)

   def __getstate__(self):
      data = {
         'parent' : self.parent(),
         'tabs' : [],
      }
      tab_list = data['tabs']
      for k in range(self.count()):
         tab_name = self.tabText(k)
         widget = self.widget(k)
         tab_list.append((widget, tab_name))
      return data

   def setup(self):
       pass

   def mouseMoveEvent(self, e):
       if e.buttons() != Qt.RightButton:
           return

       globalPos = self.mapToGlobal(e.pos())
       tabBar = self.tabBar()
       posInTab = tabBar.mapFromGlobal(globalPos)
       index = tabBar.tabAt(e.pos())
       tabBar.dragged_content = self.widget(index)
       tabBar.dragged_tabname = self.tabText(index)
       tabRect = tabBar.tabRect(index)

       pixmap = QPixmap(tabRect.size())
       tabBar.render(pixmap, QPoint(), QRegion(tabRect))
       mimeData = QMimeData()

       drag = QDrag(tabBar)
       drag.setMimeData(mimeData)
       drag.setPixmap(pixmap)

       cursor = QCursor(Qt.OpenHandCursor)

       drag.setHotSpot(e.pos() - posInTab)
       drag.setDragCursor(cursor.pixmap(), Qt.MoveAction)
       drag.exec_(Qt.MoveAction)

   def dragEnterEvent(self, e):
       e.accept()
       # self.parent().dragged_index = self.indexOf(self.widget(self.dragged_index))

   def dragLeaveEvent(self, e):
       e.accept()

   def dropEvent(self, e):
       if e.source().parentWidget() == self:
           return

       e.setDropAction(Qt.MoveAction)
       e.accept()
       tabBar = e.source()
       self.addTab(tabBar.dragged_content, tabBar.dragged_tabname)

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

