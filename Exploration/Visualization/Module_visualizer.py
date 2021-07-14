from PymoNNto.Exploration.UI_Base import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import copy
import sys
import traceback
from PymoNNto.NetworkCore.Neuron_Group import *
from PymoNNto.NetworkCore.Synapse_Group import *

from pyqtgraph.graphicsItems.GraphicsObject import GraphicsObject

import inspect

class Module_draw_item(pg.GraphicsObject):

    def __init__(self, module_name, inputs, outputs, attributes, module_type, init_vars=None, x=0, y=0, onlyff=False):
        #super().__init__(None)
        GraphicsObject.__init__(self)

        self.selected = True

        self.picture = QtGui.QPicture()

        self.draw_forward_only = onlyff

        self.conn_points = []

        self.size = 1000

        self.x = x
        self.y = y

        self.border = 0.11
        self.nob_size = 0.055

        self.module_name = module_name

        if init_vars is not None:
            self.init_vars = init_vars
        else:
            self.init_vars = [var.replace('#init', '') for var in sorted(outputs) if '#init' in var]

        self.outputs = [var.replace('#init', '') for var in sorted(outputs)]

        self.inputs = sorted(inputs)

        self.get_arrow_positions()

        self.attributes = sorted(attributes)
        self.module_type = module_type

        self.red = (237, 85, 59, 255)
        self.green = (60, 174, 163, 255)
        self.blue = (32, 99, 155, 255)
        self.yellow = (246, 213, 92, 255)

    def get_position(self, column_element_count, element_id, x_pos): #left, right, center

        if x_pos == 'left':
            x = self.x+self.border * self.size
            d=4.5

        if x_pos == 'right':
            x = self.x+ self.size - self.border * self.size
            d=4.5

        if x_pos == 'center':
            x = self.x
            d=4.5

        shift = 0
        h = self.size - self.border * self.size * d

        if column_element_count > 1:
            shift = (h / (column_element_count-1) * element_id)
        else:
            shift = h / 2.0

        y = self.y -(self.border * self.size * 1.5 + shift)
        #y = -self.border * self.size * 2 + ((1 - self.border * self.size * 4) / column_element_count * element_id)

        return x, y

    def set_font_smaller_than(self, painter, text, max_width, text_size):
        tw=max_width

        while tw >= max_width:
            qf = QFont("Arial")
            qf.setPointSizeF(text_size)

            text_size -= 0.1

            fm = QFontMetrics(qf)
            # qf.setStretch(2)
            painter.setFont(qf)
            tw = fm.width(text)

        return fm

    def draw_arrow(self, painter, pos, text, color):
        x=pos.x()
        y=pos.y()


        painter.setPen(pg.mkPen(color=color))
        painter.setBrush(pg.mkBrush(color=color))

        # painter.drawRect(QtCore.QRectF(x, y, self.nob_size * self.size, self.nob_size * self.size))

        points = QPolygonF([
            QtCore.QPointF(x - self.nob_size * self.size * 3, y - self.nob_size * self.size * 0.7),
            QtCore.QPointF(x + self.nob_size * self.size * 2, y - self.nob_size * self.size * 0.7),

            QtCore.QPointF(x + self.nob_size * self.size * 2 + self.nob_size * self.size * 0.7, y),  # arrow

            QtCore.QPointF(x + self.nob_size * self.size * 2, y + self.nob_size * self.size * 0.7),
            QtCore.QPointF(x - self.nob_size * self.size * 3, y + self.nob_size * self.size * 0.7),
            # QtCore.QPointF(x+100, y+100)
        ])

        painter.drawPolygon(points)

        painter.setPen(pg.mkPen(color=(0, 0, 0, 255)))
        painter.setBrush(pg.mkBrush(color=(0, 0, 0, 255)))

        fm = self.set_font_smaller_than(painter, text, self.nob_size * self.size * 5, self.size / 100.0 * 4.0)

        #text_size=4.0
        #tw = self.nob_size * self.size * 5

        #while tw >= self.nob_size * self.size * 5:
        #    qf = QFont("Arial")
        #    qf.setPointSizeF(self.size / 100.0 * text_size)

        #    text_size -= 0.1

        #    fm = QFontMetrics(qf)
        #    # qf.setStretch(2)
        #    painter.setFont(qf)
        #    tw = fm.width(text)


        painter.drawText(QtCore.QPointF(x - fm.width(text) / 2.0, y + fm.height() / 4), text)  # + self.nob_size * self.size / 2  float(fm.height())/20.0

        # axis.add_patch(Rectangle((x, y), nob_size, nob_size, alpha=1, color=c))
        # axis.add_patch(Circle((x + nob_size, y + nob_size / 2), 1.0 * nob_size, alpha=1, color=c))
        # axis.text(x + nob_size, y + nob_size / 2, s, fontsize=12, ha='right', va='center')

    def get_arrow_positions(self):
        self.in_pos=[]

        for i, s in enumerate(self.inputs):
            x, y = self.get_position(len(self.inputs), i, 'left')
            self.in_pos.append(QtCore.QPointF(x,y))

        self.out_pos = []
        for i, s in enumerate(self.outputs):
            x, y = self.get_position(len(self.outputs), i, 'right')
            self.out_pos.append(QtCore.QPointF(x, y))

    def add_in_out_blocks(self, painter, input_labels, output_labels):
        for s, pos in zip(self.inputs, self.in_pos):
            if s in output_labels:
                color = self.yellow
            else:
                color = self.red
            self.draw_arrow(painter, pos, s, color)

        for s, pos in zip(self.outputs,self.out_pos):
            if s in input_labels and not s in self.init_vars:
                color = self.yellow
            else:
                color = self.green
            self.draw_arrow(painter, pos, s, color)



    def draw_content(self, painter, labels):

        for i, s in enumerate(labels):

            x, y = self.get_position(len(labels), i, 'center')
            #y = -self.border * self.size * 2 + ((1 - self.border * self.size * 4) / len(labels) * i)

            color = (255, 255, 255, 255)
            painter.setPen(pg.mkPen(color=color))
            painter.setBrush(pg.mkBrush(color=color))

            qf = QFont("Arial")
            qf.setPointSizeF(self.size/100.0*4.0)

            #if ":" not in s and s!='':
            #    qf.setUnderline(True)
            #else:
            #    s='-'+s

            fm = QFontMetrics(qf)
            # qf.setStretch(2)
            painter.setFont(qf)

            painter.drawText(QtCore.QPointF(x + self.size/2-fm.width(s)/2, y+fm.height()/4), s) # + self.nob_size * self.size / 2

    def draw_connection(self, painter, from_pos, to_pos, distance, h, color):
        if distance > 0 or not self.draw_forward_only:
            from_right = QtCore.QPointF(from_pos.x() + self.nob_size * self.size * 1.0, from_pos.y())
            to_left = QtCore.QPointF(to_pos.x() - self.nob_size * self.size * 1.0, to_pos.y())
            center = QtCore.QPointF((from_pos.x() + to_pos.x()) / 2.0, (from_pos.y() + to_pos.y()) / 2.0)

            if distance != 1:

                if distance == 0:#for auto connections
                    distance=2

                if h > 0:
                    add = 200 * abs(distance)  # -200*h
                else:
                    add = -300 - 200 * abs(distance)  # -200*h

                center.setY(center.y() + add)
                from_right_2 = QtCore.QPointF(from_right.x(), (center.y() + from_right.y()) / 2.0)
                to_left_2 = QtCore.QPointF(to_left.x(), (center.y() + to_left.y()) / 2.0)
                center_left = QtCore.QPointF(from_pos.x() + self.nob_size * self.size * 2.0, center.y())
                center_right = QtCore.QPointF(to_pos.x() - self.nob_size * self.size * 2.0, center.y())

                #painter.drawLine(from_pos, from_right)
                #painter.drawLine(from_right, from_right_2)
                #painter.drawLine(from_right_2, center_left)
                #painter.drawLine(center_left, center)
                #painter.drawLine(center, center_right)
                #painter.drawLine(center_right, to_left_2)
                #painter.drawLine(to_left_2, to_left)
                #painter.drawLine(to_left, to_pos)

                pp = QPainterPath(from_pos)
                pp.quadTo(from_right, from_right_2)
                pp.quadTo(center_left, center)
                pp.quadTo(center_right, to_left_2)
                pp.quadTo(to_left, to_pos)
            else:
                pp = QPainterPath(from_pos)
                pp.quadTo(from_right, center)
                pp.quadTo(to_left, to_pos)

            if self.selected:
                color = (color[0], color[1], color[2], 255)
            else:
                color = (color[0], color[1], color[2], 100)

            painter.strokePath(pp, pg.mkPen(color=color, width=5))

    def draw_connections(self, painter, other_modules):
        points = []
        if other_modules is not None:
            self.self_index = other_modules.index(self)

            for in_indx, inp in enumerate(self.inputs):

                found = None

                #for f in range(self.self_index):
                for j in range(len(other_modules)-1):
                    f = self.self_index+1+j
                    if f>=len(other_modules)-1:
                        f=f-len(other_modules)

                    if inp in other_modules[f].outputs:
                        found = other_modules[f]


                if found is None:
                    if inp in self.outputs:
                        found = self


                if found is not None:

                    if inp in found.outputs and hasattr(found, 'out_pos'):
                        out_indx = found.outputs.index(inp)

                        from_pos = copy.copy(found.out_pos[out_indx])
                        from_pos.setX(from_pos.x()+self.nob_size*self.size*2.7)
                        to_pos = copy.copy(self.in_pos[in_indx])
                        to_pos.setX(to_pos.x()-self.nob_size*self.size*3)

                        points.append(from_pos)
                        distance = self.self_index - other_modules.index(found)

                        out_h = (len(found.outputs) + 1) / 2 - (found.outputs.index(inp) + 1)
                        inp_h = (len(self.inputs) + 1) / 2 - (self.inputs.index(inp) + 1)
                        h = out_h + inp_h

                        color = self.yellow
                        if inp in found.init_vars:
                            color = self.green
                            if found == self:
                                color = (0, 0, 0, 50)

                        self.draw_connection(painter, from_pos, to_pos, distance, h, color)

        return points


    def update_pic(self, other_modules=None):
        self.picture = QtGui.QPicture()
        painter = QtGui.QPainter(self.picture)
        painter.scale(1, -1)

        self.conn_points = self.draw_connections(painter, other_modules)

        color = self.blue
        #if self.selected:
        #    painter.setPen(pg.mkPen(color=(0,0,0,255), width=10))
        #else:

        if self.selected:
            color = (color[0], color[1], color[2], 255)
        else:
            color = (color[0], color[1], color[2], 100)

        painter.setPen(pg.mkPen(color=(0, 0, 0, 0)))
        painter.setBrush(pg.mkBrush(color=color))

        #currentAxis.plot([0, 0, 1.0 + border], [0, 1, 1], color='white')

        painter.drawRect(QtCore.QRectF(self.x+self.border*self.size, self.y-self.size+self.border*self.size, self.size - self.border * self.size * 2, self.size - self.border * self.size * 2))

        color = (255, 255, 255, 255)
        painter.setPen(pg.mkPen(color=color))
        painter.setBrush(pg.mkBrush(color=color))



        text = self.module_name.replace('_', ' ')
        fm = self.set_font_smaller_than(painter, text, self.size - self.border * self.size * 3, text_size=self.size/100.0*7.0)

        #qf = QFont("Arial")
        #qf.setPointSizeF(self.size/100.0*7.0)
        #qf.setUnderline(True)
        #qf.setBold(True)
        #fm = QFontMetrics(qf)
        # qf.setStretch(2)
        #painter.setFont(qf)

        painter.drawText(int(self.x+0.5*self.size-fm.width(text)/2), self.y-int(self.size - self.border * self.size * 1.5-fm.height()/2), text)

        qf = QFont("Arial")
        #qf.setLetterSpacing(QFont.PercentageSpacing, 95)
        qf.setPointSizeF(self.size/100.0*1.5)
        fm = QFontMetrics(qf)
        # qf.setStretch(2)
        painter.setFont(qf)
        text = self.module_type
        painter.drawText(int(self.x+0.5 * self.size - fm.width(text) / 2), int(self.y-self.border * self.size*1.2 + fm.height() / 2), text)

        self.add_in_out_blocks(painter, self.inputs, self.outputs)

        if len(self.attributes) > 0:
            self.draw_content(painter, ['', '']+self.attributes+['', 'Attributes:'])#Initialization a



        painter.end()
        self.prepareGeometryChange()
        self.informViewBoundsChanged()


    def paint(self, painter, option, widget=None):
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        br = self.picture.boundingRect()
        br.setLeft(self.x)  # min(br.top()-10, br.left()-10)
        br.setTop(-self.y+self.border*self.size)#max(br.top()-10, br.left()-10)
        br.setRight(self.x+self.size)#,max(br.right()+10, br.bottom()+10)
        br.setBottom(-self.y+self.size-self.border*self.size)#,max(br.right()+10, br.bottom()+10)

        #for p in self.conn_points:
        #    if p.x() < br.left(): br.setLeft(p.x())
        #    if p.y() < br.top(): br.setTop(p.y())
        #    if p.x() > br.right(): br.setRight(p.x())
        #    if p.y() > br.bottom(): br.setBottom(p.y())

        #print(br.left(), br.top(), br.right(), br.bottom())
        return QtCore.QRectF(br)


class module_drawer(UI_Base):

    def __init__(self):
        super().__init__(None, label='Drawer', create_sidebar=False)

        pg.setConfigOptions(antialias=True)

        self.main_window.setGeometry(10, 40, 714, 608)

        self.di_modules = []

    def add_flow_chart(self, ff_only=False):
        self.flow_tab = self.Next_Tab('Flow_Chart', stretch=0.0)
        self.flow_tab.plot = self.Add_plot()
        self.flow_tab.plot.hideAxis('bottom')
        self.flow_tab.plot.hideAxis('left')
        self.flow_tab.modules = []

        self.x = 0
        self.y = 0

        def on_plot_click_event(event):
            for mod in self.flow_tab.modules:
                mod.selected = True

            for mod in self.flow_tab.modules:
                mod.update_pic(self.flow_tab.modules)

            self.flow_tab.plot.update()

        self.flow_tab.plot.mouseClickEvent = on_plot_click_event

        for mod in self.di_modules:
            mdi = Module_draw_item(mod.module_name, mod.inputs, mod.outputs, mod.attributes, mod.module_type, mod.init_vars, self.x, self.y, ff_only)

            self.flow_tab.modules.append(mdi)
            self.flow_tab.plot.addItem(mdi)

            def on_mod_click_event(event):
                for mod in self.flow_tab.modules:
                    mod.selected = False

                event.currentItem.selected = True

                for mod in self.flow_tab.modules:
                    mod.update_pic(self.flow_tab.modules)
                self.flow_tab.plot.update()

            mdi.mouseClickEvent = on_mod_click_event

            self.x += 1200
            # self.y += 1200

        for mod in self.flow_tab.modules:
            mod.update_pic(self.flow_tab.modules)
        self.flow_tab.plot.update()



    def add_module_tab(self, module_name, inputs, outputs, attributes, module_type):

        self.main_tab = self.Next_Tab(module_name, stretch=0.0)
        self.main_tab.plot = self.Add_plot()

        mdi = Module_draw_item(module_name, inputs, outputs, attributes, module_type)
        self.main_tab.draw_item = mdi
        self.di_modules.append(mdi)
        self.main_tab.plot.addItem(mdi)

        #def mce(event):
        #    print('dfsgsdfgdf')
        #mdi.mouseClickEvent = mce

        #self.main_tab.plot.setXRange(-5, 5)
        #self.main_tab.plot.sigXRangeChanged.connect(lambda _, t: self.main_tab.plot.setYRange(*t))

        self.main_tab.draw_item.update_pic(None)
        self.main_tab.plot.hideAxis('bottom')
        self.main_tab.plot.hideAxis('left')

        self.main_tab.plot.update()


    def add_module(self, module):
        from PymoNNto.NetworkCore.Neuron_Group import NeuronGroup
        from PymoNNto.NetworkCore.Synapse_Group import SynapseGroup

        module_copy = copy.deepcopy(module)

        ng = NeuronGroup_read_write_event(1, {}, None)
        sg = SynapseGroup_read_write_event(ng, ng, None)

        main_arg = ng
        module_type = 'PymoNNto Neuron-Group Module'
        synapse_beh_arg_names = ['s', 'S', 'syn', 'Syn', 'SYN', 'syns', 'Syns', 'SYNS', 'synapse', 'Synapse', 'SYNAPSE', 'synapses', 'Synapses', 'SYNAPSES']
        func1_arg_names = inspect.getfullargspec(module_copy.set_variables).args
        func2_arg_names = inspect.getfullargspec(module_copy.new_iteration).args
        for s in synapse_beh_arg_names:
            if s in func1_arg_names or s in func2_arg_names:
                main_arg = sg
                module_type = 'PymoNNto Synapse-Group Module'

        if module_copy.set_variables_on_init:
            module_type += ' (init set var)'


        #ng = NeuronGroup(1, {}, None)
        #sg = SynapseGroup(ng, ng, None)

        ng.afferent_synapses['All']=[sg]
        ng.efferent_synapses['All']=[sg]

        #print(module_copy, ng.__dict__)

        def reset_vars():
            ng.variable_reads = []
            ng.variable_writes = []
            sg.variable_reads = []
            sg.variable_writes = []

        reset_vars()

        #delattr(sg, 'enabled')

        def read_ng(obj, attr):
            obj.variable_reads.append('n.'+attr)

        def write_ng(obj, attr):
            obj.variable_writes.append('n.'+attr)

        def read_sg(obj, attr):
            obj.variable_reads.append('s.'+attr)

        def write_sg(obj, attr):
            obj.variable_writes.append('s.'+attr)

        #set_read_event_function(ng, read_ng)
        #set_write_event_function(ng, write_ng)

        #set_read_event_function(sg, read_sg)
        #set_write_event_function(sg, write_sg)

        ng.set_read_event_function(read_ng)
        ng.set_write_event_function(write_ng)

        sg.set_read_event_function(read_sg)
        sg.set_write_event_function(write_sg)


        created_vars_set = analyze_function(module_copy, 'set_variables', ng, sg, main_arg)
        write_vars_set = ng.variable_writes + sg.variable_writes#[var for var in ng.variable_writes + sg.variable_writes if var not in created_vars_set]
        read_vars_set = ng.variable_reads + sg.variable_reads#[var for var in ng.variable_reads + sg.variable_reads if var not in created_vars_set]

        #print(module_copy, created_vars_set)

        reset_vars()

        created_vars_it = analyze_function(module_copy, 'new_iteration', ng, sg, main_arg)
        write_vars_it = ng.variable_writes + sg.variable_writes#[var for var in ng.variable_writes + sg.variable_writes if var not in created_vars_it]
        read_vars_it = ng.variable_reads + sg.variable_reads#[var for var in ng.variable_reads + sg.variable_reads if var not in created_vars_it]

        inputs = list(set(read_vars_it + write_vars_it + created_vars_it)) #read_vars_set
        outputs_temp = list(set(write_vars_set + write_vars_it + created_vars_set + created_vars_it))#created_vars_it #[var+'#init' for var in created_vars_set]

        outputs = []
        for o in outputs_temp:
            if o in created_vars_set:
                outputs.append(o+'#init')
                #print(module_copy, o)
            else:
                outputs.append(o)
            #outputs = [var+'#init' for var in outputs if var in created_vars_set]

        #inputs = list(set(ng.variable_reads + sg.variable_reads + created_vars_it))
        #outputs = list(set(ng.variable_writes + sg.variable_writes+created_vars_set + created_vars_it))


        module_name = module_copy.__class__.__name__

        attributes = module_copy.used_attr_keys.copy()  # ['transmitter', 'test', 'blub', 'param', 'dfsfa']
        if 'tag' in attributes:
            attributes.remove('tag')
        if 'behaviour_enabled' in attributes:
            attributes.remove('behaviour_enabled')
          # self.parent.__class__.__name__ + ' Module'

        #inputs = list(set(read_vars_set + read_vars_it))
        #outputs = list(set(write_vars_set + write_vars_it))

        attributes = list(set(attributes))

        if hasattr(module_copy, 'visualization_module_inputs') and module_copy.visualization_module_inputs is not None:
            inputs = module_copy.visualization_module_inputs

        if hasattr(module_copy, 'visualization_module_outputs') and module_copy.visualization_module_outputs is not None:
            outputs = module_copy.visualization_module_outputs

        if hasattr(module_copy, 'visualization_module_attributes') and module_copy.visualization_module_attributes is not None:
            attributes = module_copy.visualization_module_attributes


        #filter
        filter = ['n.iteration', 's.iteration']
        inputs = [var for var in inputs if not var in filter]
        outputs = [var for var in outputs if not var in filter]
        attributes = [var for var in attributes if not var in filter]

        self.add_module_tab(module_name, inputs, outputs, attributes, module_type)


def set_read_event_function(object, ref):
    object.current_dict = copy.copy(dir(object))
    object.ref = ref

    def __getattr__(self, attr_name):
        if attr_name in ['wef', 'ref', 'current_dict'] or self.current_dict is None or attr_name in self.current_dict:
            return super().__getattribute__(attr_name)
        self.ref(self, attr_name)
        return super().__getattribute__(attr_name)#self.get_neuron_vec('uniform')

    def __getattribute__(self, attr_name):
        if attr_name in ['wef', 'ref', 'current_dict'] or self.current_dict is None or attr_name in self.current_dict:
            return super().__getattribute__(attr_name)
        self.ref(self, attr_name)
        return super().__getattribute__(attr_name)#self.get_neuron_vec('uniform')

    object.__getattr__ = __getattr__
    object.__getattribute__ = __getattribute__


def set_write_event_function(object, wef):
    object.current_dict = copy.copy(dir(object))
    object.wef = wef

    def __setattr__(self, attr_name, val):
        if self.wef is not None:
            self.wef(self, attr_name)
        super().__setattr__(attr_name, val)

    object.__setattr__ = __setattr__


class NeuronGroup_read_write_event(NeuronGroup):

    ref = None
    wef = None
    current_dict = None

    def set_read_event_function(self, ref):
        self.current_dict = copy.copy(dir(self))
        self.ref = ref

    def set_write_event_function(self, wef):
        self.current_dict = copy.copy(dir(self))
        self.wef = wef

    def __getattr__(self, attr_name):
        if attr_name in ['wef', 'ref', 'current_dict'] or self.current_dict is None or attr_name in self.current_dict:
            return super().__getattribute__(attr_name)
        self.ref(self, attr_name)
        return super().__getattribute__(attr_name)#self.get_neuron_vec('uniform')

    def __getattribute__(self, attr_name):
        if attr_name in ['wef', 'ref', 'current_dict'] or self.current_dict is None or attr_name in self.current_dict:
            return super().__getattribute__(attr_name)
        self.ref(self, attr_name)
        return super().__getattribute__(attr_name)#self.get_neuron_vec('uniform')

    def __setattr__(self, attr_name, val):
        if self.wef is not None:
            self.wef(self, attr_name)
        super().__setattr__(attr_name, val)

class SynapseGroup_read_write_event(SynapseGroup):

    ref = None
    wef = None
    current_dict = None

    def set_read_event_function(self, ref):
        self.current_dict = copy.copy(dir(self))
        self.ref = ref

    def set_write_event_function(self, wef):
        self.current_dict = copy.copy(dir(self))
        self.wef = wef

    def __getattr__(self, attr_name):
        if attr_name in ['wef', 'ref', 'current_dict'] or self.current_dict is None or attr_name in self.current_dict:
            return super().__getattribute__(attr_name)
        self.ref(self, attr_name)
        return super().__getattribute__(attr_name)#self.get_synapse_mat('uniform')

    def __getattribute__(self, attr_name):
        if attr_name in ['wef', 'ref', 'current_dict'] or self.current_dict is None or attr_name in self.current_dict:
            return super().__getattribute__(attr_name)
        self.ref(self, attr_name)
        return super().__getattribute__(attr_name)#self.get_synapse_mat('uniform')

    def __setattr__(self, attr_name, val):
        if self.wef is not None:
            self.wef(self, attr_name)
        super().__setattr__(attr_name, val)

def analyze_function(object, function_name, ng, sg, arg):
    ng_dict_backup = copy.copy(ng.__dict__)
    sg_dict_backup = copy.copy(sg.__dict__)

    finished = False
    used_variable_keys_ng = []
    used_variable_keys_sg = []

    while not finished:
        try:
            getattr(object, function_name)(arg)

            finished = True
        except Exception as e:
            error_type = sys.exc_info()[0]
            msg = str(sys.exc_info()[1])
            #print(error_type, msg)
            if str(error_type.__name__) == 'AttributeError':
                sp = msg.split("'")
                if len(sp) > 3:
                    key = sp[3]

                    if 'SynapseGroup_read_write_event' in msg:
                        used_variable_keys_sg.append('s.'+key)
                        var = sg.get_synapse_mat()
                        setattr(sg, key, var)

                    elif 'NeuronGroup_read_write_event' in msg:
                        used_variable_keys_ng.append('n.'+key)
                        var = ng.get_neuron_vec()
                        setattr(ng, key, var)

            elif str(error_type.__name__) == 'KeyError':
                tag=msg.replace("'", '')
                ng.afferent_synapses[tag] = [sg]
                ng.efferent_synapses[tag] = [sg]

            elif 'invalid value encountered' in msg:
                print('yes')

            else:
                #print(error_type, msg)
                traceback.print_tb(e.__traceback__)
                print('failed to analyse module automatically')
                finished = True

    created_variables_ng = ['n.'+var for var in ng.__dict__ if var not in ng_dict_backup]
    created_variables_sg = ['s.'+var for var in sg.__dict__ if var not in sg_dict_backup]

    return created_variables_ng+created_variables_sg #used_variable_keys_ng+used_variable_keys_sg+





