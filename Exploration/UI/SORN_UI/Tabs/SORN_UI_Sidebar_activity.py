from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np
#from Testing.SORN.SORN_Helper import *

#import matplotlib.pyplot as plt

class SORN_UI_sidebar_activity_module():

    def add_recorder_variables(self, neuron_group, recorder):
        return

    def initialize(self, SORN_UI, index):

        #self.group_select_box = QComboBox()

        #def group_changed(event):
        #    SORN_UI.neuron_select_id = 0
        #    SORN_UI.ts_group = self.group_select_box.currentIndex()

        # self.group_select_box.mousePressEvent=click
        #self.group_select_box.currentIndexChanged.connect(group_changed)

        #for i in range(np.max([len(SORN_UI.network[group_tag]) for group_tag in SORN_UI.group_tags])):
        #    self.group_select_box.addItem('Timescale' + str(i))

        # self.input_select_box.addItem("Prediction")
        # self.input_select_box.addItem("None")
        #SORN_UI.Add_Sidebar_Element(self.group_select_box)

        def mce(event):
            SORN_UI.neuron_select_group = event.currentItem.neuron_group_tag
            w = SORN_UI.network[SORN_UI.neuron_select_group,0].width
            h = SORN_UI.network[SORN_UI.neuron_select_group,0].height
            SORN_UI.neuron_select_y = np.clip(int((h-1)-np.trunc(event.pos().y())), 0, h - 1)
            SORN_UI.neuron_select_x = np.clip(int(np.trunc(event.pos().x())), 0, w - 1)
            SORN_UI.neuron_select_id = SORN_UI.neuron_select_y * w + SORN_UI.neuron_select_x
            SORN_UI.static_update_func()

        group_select_box=QComboBox()
        SORN_UI.Add_Sidebar_Element(group_select_box)

        SORN_UI.group_sliders.append(QSlider(1))  # QtCore.Horizontal
        SORN_UI.group_sliders[-1].setMinimum(0)
        SORN_UI.group_sliders[-1].setMaximum(100)
        SORN_UI.group_sliders[-1].setSliderPosition(100)
        SORN_UI.group_sliders[-1].mouseReleaseEvent = SORN_UI.static_update_func

        SORN_UI.sidebar_hblock.addWidget(SORN_UI.group_sliders[-1])

        self.image_item = SORN_UI.Add_Image_Item(False, True)
        self.image_item.neuron_group_tag = SORN_UI.group_tags[index]
        SORN_UI.neuron_visible_groups.append(SORN_UI.group_tags[index])
        self.image_item.mouseClickEvent = mce

        def group_changed(select_index):
            tag=SORN_UI.group_tags[select_index]
            SORN_UI.neuron_select_group = tag
            self.image_item.neuron_group_tag = tag
            SORN_UI.neuron_visible_groups[index] = tag
            SORN_UI.neuron_select_id = 0

        group_select_box.addItems(SORN_UI.group_tags)
        group_select_box.setCurrentIndex(index)
        group_select_box.currentIndexChanged.connect(group_changed)



    def update(self, SORN_UI):

        #for group_tag in SORN_UI.group_tags:
        group_tag = self.image_item.neuron_group_tag
        if len(SORN_UI.network[group_tag]) > 0:

            group = SORN_UI.network[group_tag, 0]
            shape = (group.height, group.width)

            if hasattr(group, 'color'):
                a = group.color[3] / 255.0
                c = (group.color[0] / 255.0 * a, group.color[1] / 255.0 * a, group.color[2] / 255.0 * a)
            else:
                c=(0.0, 0.0, 1.0)

            if hasattr(group, 'display_min_max_act'):
                levels = group.display_min_max_act
            else:
                levels = (0, 1)

            c=(c[0]*levels[1],c[1]*levels[1],c[2]*levels[1])

            r = np.ones(group.size) * c[0] #b.copy()  # np.zeros(b.shape)
            g = np.ones(group.size) * c[1] #b.copy()  # np.zeros(b.shape)
            b = np.ones(group.size) * c[2] #group.output.copy()

            if hasattr(group, 'Input_Mask'):
                r[group.Input_Mask] = (c[0] * 0.5)#0.3
                g[group.Input_Mask] = (c[1] * 0.5)#0.3
                b[group.Input_Mask] = (c[2] * 0.5)#0.3

            if hasattr(group, 'output'):
                r = np.clip(r + group.output, 0, 1)
                g = np.clip(g + group.output, 0, 1)
                b = np.clip(b + group.output, 0, 1)

            if SORN_UI.neuron_select_group == group_tag:
                r[SORN_UI.neuron_select_id] = 0
                g[SORN_UI.neuron_select_id] = max(0.8, g[SORN_UI.neuron_select_id])
                b[SORN_UI.neuron_select_id] = 0

            image = np.dstack((np.reshape(r, shape), np.reshape(g, shape), np.reshape(b, shape)))



            self.image_item.setImage(np.rot90(image, 3), levels=levels)

class SORN_UI_sidebar_activity():

    def __init__(self, group_display_count):
        self.group_display_count=group_display_count

    def add_recorder_variables(self, neuron_group, recorder):
        for module in self.sub_modules:
            module.add_recorder_variables(neuron_group, recorder)

    def initialize(self, SORN_UI):

        if SORN_UI.group_display_count is not None:
            self.group_display_count=SORN_UI.group_display_count

        self.sub_modules = []
        for i in range(self.group_display_count):
            self.sub_modules.append(SORN_UI_sidebar_activity_module())
            self.sub_modules[-1].initialize(SORN_UI, np.minimum(i, len(SORN_UI.group_tags)))

    def update(self, SORN_UI):
        for module in self.sub_modules:
            module.update(SORN_UI)