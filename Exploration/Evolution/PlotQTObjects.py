from PymoNNto.Exploration.Network_UI.TabBase import *
from PymoNNto.Exploration.StorageManager.StorageManager import *
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np


#UI_base.Add_element(InteractiveScatter(...), sidebar, stretch)
class InteractiveScatter(pg.GraphicsLayoutWidget):#canvas object

    def __init__(self,default_x='index', default_y='score', coloration_param='list', *args, **kwargs):#
        super().__init__(*args, **kwargs)

        self.default_x = default_x
        self.default_y = default_y
        self.coloration_param = coloration_param
        self.global_coloration = True

        self.storage_manager_groups = []

        self.initialize_plot()

        self.scatter_clicked_event = None
        self.scatter_double_clicked_event = None


    def scatter_clicked(self, plot, points):
        print('clicked')
        if len(points) > 0:
            self.clicked_generation = points[-1]._data[0]
            self.clicked_score = points[-1]._data[1]

            self.clicked_sm = points[-1]._data[3]
            self.clicked_smg = points[-1]._data[4]
            print(self.clicked_sm)

            self.scatter2.setData(x=[self.clicked_generation], y=[self.clicked_score])  # set second scatter to new selection
            self.scatter2.data[0][3] = self.clicked_sm
            if self.scatter_clicked_event is not None:
                self.scatter_clicked_event(self.clicked_sm)

    def scatter_double_clicked(self, plot, points):#scatter2

        print('double clicked', self.clicked_sm)

        #evo_id = tab.data[-3, tab.clicked_sm][0]
        # print(evo_id)

        sm = self.clicked_sm#self.clicked_smg['id==' + str(int(self.clicked_sm))][0]

        txt = open(sm.absolute_path + sm.config_file_name, 'r').read()

        layout = QVBoxLayout()
        pte = QPlainTextEdit()
        pte.setPlainText(txt)
        pte.setReadOnly(True)
        layout.addWidget(pte)

        dlg = QDialog()
        #dlg.setWindowTitle(sm.absolute_path + sm.config_file_name)
        dlg.setLayout(layout)
        dlg.resize(1200, 800)
        dlg.exec()

        if self.scatter_double_clicked_event is not None:
            self.scatter_double_clicked_event(self.clicked_sm)

    def change_axis_param(self, axis_name, param):

        dx = self.default_x
        dy = self.default_y
        dc = self.coloration_param

        try:
            if axis_name == 'bottom':
                self.default_x = param
                self.plot.getAxis(axis_name).setLabel(text=param)

            if axis_name == 'left':
                self.default_y = param
                self.plot.getAxis(axis_name).setLabel(text=param)

            if axis_name == 'color':
                self.coloration_param = param

            self.refresh_data()

            return param
        except:
            self.default_x = dx
            self.default_y = dy
            self.coloration_param = dc



    def get_all_params(self):
        result_dict = {}
        for smg in self.storage_manager_groups:
            for param in smg.get_all_params():
                result_dict[param] = True
        return result_dict.keys()


    def axis_dialog(self, axis_name):
        dlg = QDialog()
        dlg.setWindowTitle('Select ' + axis_name + ' axis parameter')
        layout = QVBoxLayout()

        listwidget = QListWidget()

        if axis_name=='color':
            listwidget.addItems(['list'])

        listwidget.addItems(self.get_all_params())

        layout.addWidget(listwidget)

        def btn_clicked():
            self.change_axis_param(axis_name, listwidget.currentItem().text())
            dlg.close()

        btn = QPushButton('set new axis parameter')
        btn.clicked.connect(btn_clicked)

        layout.addWidget(btn)
        dlg.setLayout(layout)
        dlg.resize(300, 300)
        dlg.exec()


    def initialize_plot(self):
        self.setBackground((255, 255, 255))

        #if tooltip_message is not None:
        #    self.ci.setToolTip(tooltip_message)

        self.clicked_generation = -1
        self.clicked_score = -1
        self.clicked_sm = None
        self.clicked_smg = ''

        self.plot = self.addPlot(row=0, col=0)#, axisItems=axisItems
        #self.plot.addLegend()

        #tab.item = pg.FillBetweenItem(curve1=tab.curves[1], curve2=tab.curves[2], brush=(255, 0, 0, 100))
        #tab.plot.addItem(tab.item)

        # trendline
        self.mean_line = pg.PlotCurveItem([],pen=(0,0,0,255))
        self.plot.addItem(self.mean_line)

        # minmax area
        self.max_line = pg.PlotCurveItem([],pen=(0,0,0,255))
        self.plot.addItem(self.max_line)

        self.min_line = pg.PlotCurveItem([],pen=(0,0,0,255))
        self.plot.addItem(self.min_line)

        self.min_max_fill = pg.FillBetweenItem(curve1=self.max_line, curve2=self.min_line, brush=(0, 0, 0, 30))
        self.plot.addItem(self.min_max_fill)

        #on click highlight scatter item
        self.scatter2 = pg.ScatterPlotItem(size=10, brush=pg.mkBrush(0, 0, 255, 255))
        self.plot.addItem(self.scatter2)
        self.scatter2.sigClicked.connect(self.scatter_double_clicked)


        self.plot.getAxis('bottom').setLabel(text=self.default_x)
        self.plot.getAxis('left').setLabel(text=self.default_y)

        def bottom_axis_clicked(ev):
            self.axis_dialog('bottom')

        self.plot.getAxis('bottom').mouseClickEvent = bottom_axis_clicked

        def left_axis_clicked(ev):
            self.axis_dialog('left')

        self.plot.getAxis('left').mouseClickEvent = left_axis_clicked




    def find_same_path_smg(self, smg):
        found = None
        for attached_smg in self.storage_manager_groups:
            if smg.absolute_path == attached_smg.absolute_path:
                found = attached_smg

        return found

    def remove_StorageManagerGroup(self, smg):
        found = self.find_same_path_smg(smg)
        if found is not None:
            self.storage_manager_groups.remove(found)
            self.plot.removeItem(found.scatter)
            self.update_indices()
            self.scatter2.clear()

    def get_smg(self, tag):
        for smg in self.storage_manager_groups:
            if smg.Tag == tag:
                return smg

    def add_StorageManagerGroup(self, smg):

        found = self.find_same_path_smg(smg)

        if found is None:
            smg.scatter = pg.ScatterPlotItem(size=10, name=smg.Tag)#, brush=pg.mkBrush(np.random.randint(0,255), np.random.randint(0,255), 255, 120)
            smg.scatter.sigClicked.connect(self.scatter_clicked)
            #self.plot.legend.addItem(smg.scatter, smg.Tag)
            self.plot.addItem(smg.scatter)
        else:
            smg.scatter = found.scatter
            smg.color = found.color
            self.storage_manager_groups.remove(found)

        if not hasattr(smg, 'color'):
            smg.color = (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))

            #print('ck', smg.color[0], smg.color[1], smg.color[2], 120)
            #color = pg.mkBrush(smg.color[0], smg.color[1], smg.color[2], 120)
            #color = pg.mkBrush(np.random.randint(0, 255), np.random.randint(0, 255), 255, 120)
            #smg.scatter.setData(brush=color)

        self.storage_manager_groups.append(smg)

        self.update_indices()

        self.plot.removeItem(self.scatter2)#bring to front
        self.plot.addItem(self.scatter2)
        self.scatter2.clear()


    def update_indices(self):
        return
        #for i, smg in enumerate(self.storage_manager_groups):
        #    smg.add_virtual_multi_parameter('index', i)

    def add_trendline(self, smg):
        if self.default_x=='gen':
            result_lists = smg.get_multi_param_list([self.default_x, self.default_y], remove_None=True).astype(np.float64)

            xa, ya = smg.remove_duplicates_get_eval(result_lists[-2], result_lists[-1], evalstr='np.average(a)')
            xs, ymi = smg.remove_duplicates_get_eval(result_lists[-2], result_lists[-1], evalstr='np.min(a)')
            xs, yma = smg.remove_duplicates_get_eval(result_lists[-2], result_lists[-1], evalstr='np.max(a)')

            self.mean_line.setData(xa, ya)
            self.min_line.setData(xa, ymi)
            self.max_line.setData(xa, yma)

            self.mean_line.setVisible(True)
            self.min_line.setVisible(True)
            self.max_line.setVisible(True)
            self.min_max_fill.setVisible(True)
        else:
            self.mean_line.setVisible(False)
            self.min_line.setVisible(False)
            self.max_line.setVisible(False)
            self.min_max_fill.setVisible(False)

    def refresh_data(self):
        single_smg = len(self.storage_manager_groups)==1

        #refresh and get global min max color
        color_vals = []
        for smg in self.storage_manager_groups:
            if self.coloration_param != 'list' and self.global_coloration:
                color_vals += smg.get_param_list(self.coloration_param, remove_None=True)

            smg.refresh()

        #actual refresh
        for smg in self.storage_manager_groups:

            params=['#SM#', self.default_x, self.default_y]

            if self.coloration_param != 'list':
                params += [self.coloration_param]

            data = smg.get_multi_param_list(params, remove_None=True)

            if self.coloration_param == 'list':
                c = pg.mkBrush(smg.color[0], smg.color[1], smg.color[2], 120)
            else:
                if self.global_coloration:
                    min=np.min(color_vals)
                    max=np.max(color_vals)
                else:
                    min=np.min(data[3])
                    max=np.max(data[3])
                d=max-min
                if d==0:
                    d=1
                c=[pg.mkBrush(255-255/d*(c-min), 255/d*(c-min), 0, 120) for c in data[3]]

            smg.scatter.setData(x=data[1], y=data[2], brush=c)  #

            for i, d in enumerate(smg.scatter.data):  # set ids to each point (d[3] very ugly coding...) (each point is a set, not an object)
                d[3] = data[0][i]
                d[4] = smg

        self.scatter2.clear()

        if single_smg:
            self.add_trendline(self.storage_manager_groups[0])


















class Radar_Plot(pg.GraphicsLayoutWidget):

    def __init__(self, genome_alphabet, *args, **kwargs):  #
        super().__init__(*args, **kwargs)

        tab.radar_plot = ui.Add_plot(x_label='radar plot',tooltip_message='radar plot of the last genomes. (green=high score/red=low score/blue=selected)')  # axisItems={'left': stringaxis}
        tab.draw_item = DrawItem2()
        tab.radar_plot.addItem(tab.draw_item)

        def val_changed():
            if hasattr(tab, 'data'):
                tab.draw_item.update_pic(tab.gene_keys, tab.data, tab.clicked_id, tab.slider.value())

        tab.slider = ui.Add_element(QSlider(Qt.Vertical))
        tab.slider.setMinimum(10)
        tab.slider.setMaximum(5000)
        tab.slider.setValue(100)
        tab.slider.valueChanged.connect(val_changed)

        tab.radar_plot.hideAxis('bottom')
        tab.radar_plot.hideAxis('left')


