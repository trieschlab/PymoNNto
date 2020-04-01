from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np

import sys

from PyQt5 import QtCore, QtGui, QtWidgets, uic

import pyqtgraph as pg

class DrawItem(pg.GraphicsObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.picture = QtGui.QPicture()
        #self.update()

    #@property
    #def rect(self):
    #    return self._rect

    def get_rnd_color(self):
        return (np.random.rand()*255.0,np.random.rand()*255.0,np.random.rand()*255.0,255.0)

    def update_pic(self, sub_sg):
        self.picture = QtGui.QPicture()
        painter = QtGui.QPainter(self.picture)
        middle=int(len(sub_sg)/2)

        for i,sg in enumerate(sub_sg):
            painter.setPen(pg.mkPen(color=(0,0,0,255)))
            if i==0:
                painter.setBrush(pg.mkBrush(color=sg.src.color))
            else:
                painter.setBrush(pg.mkBrush(color=(0,0,0,0)))
            minx=np.min(sg.src.x)
            miny=np.min(sg.src.y)
            maxx=np.max(sg.src.x)
            maxy=np.max(sg.src.y)
            painter.drawRect(QtCore.QRect(minx, miny, maxx-minx, maxy-miny))

            painter.setPen(pg.mkPen("w"))
            painter.setBrush(pg.mkBrush(color=sg.dst.color))
            minx=np.min(sg.dst.x)
            miny=np.min(sg.dst.y)
            maxx=np.max(sg.dst.x)
            maxy=np.max(sg.dst.y)
            painter.drawRect(QtCore.QRect(50+minx, miny, maxx-minx, maxy-miny))

        painter.end()
        #self.update()

    def paint(self, painter, option, widget=None):
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())


class SORN_partition_tab():

    def add_recorder_variables(self, neuron_group, recorder):
        return

    def initialize(self, SORN_UI):
        self.partition_tab = SORN_UI.Next_Tab('partition')

        self.draw_items = {}
        self.plots = {}
        for transmitter in SORN_UI.transmitters:
            self.plots[transmitter] = SORN_UI.Add_plot()
            self.draw_items[transmitter] = DrawItem()
            self.plots[transmitter].addItem(self.draw_items[transmitter])

    def update(self, SORN_UI):
        if self.partition_tab.isVisible():
            group=SORN_UI.network[SORN_UI.neuron_select_group, 0]
            for transmitter in SORN_UI.transmitters:
                self.draw_items[transmitter].update_pic(group.afferent_synapses[transmitter])
                self.plots[transmitter].update()

            #self.plot.refresh()