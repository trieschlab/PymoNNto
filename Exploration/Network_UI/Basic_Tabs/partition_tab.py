from PymoNNto.Exploration.Network_UI.TabBase import *

class DrawItem(pg.GraphicsObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.picture = QtGui.QPicture()

    def get_rnd_color(self):
        return (np.random.rand()*255.0,np.random.rand()*255.0,np.random.rand()*255.0,255.0)

    def get_rect(self, ng, x_shift=0, y_shift=0):
        minx = np.min(ng.x)
        miny = np.min(ng.y)
        maxx = np.max(ng.x)
        maxy = np.max(ng.y)
        return QtCore.QRectF(minx + x_shift, miny+y_shift, maxx - minx, maxy - miny)

    def draw_input_output_block(self, painter, sg, fill=False, y_shift=0):
        painter.setPen(pg.mkPen(color=(0, 0, 0, 255)))
        if fill:
            painter.setBrush(pg.mkBrush(color=sg.src.color))
        else:
            painter.setBrush(pg.mkBrush(color=(0, 0, 0, 0)))
        painter.drawRect(self.get_rect(sg.src, -30, y_shift))

        painter.setPen(pg.mkPen(color=(0, 0, 0, 255)))
        if fill:
            painter.setBrush(pg.mkBrush(color=sg.dst.color))
        else:
            painter.setBrush(pg.mkBrush(color=(0, 0, 0, 0)))
        sg.dst_position_rect=self.get_rect(sg.dst, 30.0)
        painter.drawRect(sg.dst_position_rect)


    def update_pic(self, sub_sgs, group):

        blocks = {}

        for sg in sub_sgs:
            if not sg.src.BaseNeuronGroup in blocks:
                blocks[sg.src.BaseNeuronGroup]=[]
            blocks[sg.src.BaseNeuronGroup].append(sg)

        self.sub_sgs=sub_sgs

        self.picture = QtGui.QPicture()
        painter = QtGui.QPainter(self.picture)

        painter.setPen(pg.mkPen(color=(0, 0, 0, 100)))
        painter.setBrush(pg.mkBrush(color=(0, 0, 0, 0)))

        for x,y in zip(group.x, group.y):
            painter.drawEllipse(QtCore.QPointF(x+30, y), 0.4, 0.4)

        if len(sub_sgs)>0:
            for x,y in zip(sub_sgs[0].src.BaseNeuronGroup.x,sub_sgs[0].src.BaseNeuronGroup.y):
                painter.drawEllipse(QtCore.QPointF(x-30, y), 0.4, 0.4)

        for i, key in enumerate(blocks):
            for sg in blocks[key]:
                if hasattr(sg, 'selected') and sg.selected:
                    self.draw_input_output_block(painter, sg, True, 30*i)

        for i, key in enumerate(blocks):
            for sg in blocks[key]:
                self.draw_input_output_block(painter, sg, False, 30*i)

        painter.drawPolygon(QtCore.QPoint(0,1),
                            QtCore.QPoint(0,2),
                            QtCore.QPoint(3,0),
                            QtCore.QPoint(0,-2),
                            QtCore.QPoint(0,-1),
                            QtCore.QPoint(-4,-1),
                            QtCore.QPoint(-4,1))

        painter.end()
        self.prepareGeometryChange()
        self.informViewBoundsChanged()

    def paint(self, painter, option, widget=None):
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        br=self.picture.boundingRect()
        br.setTop(min(br.top(), br.left()))
        br.setLeft(min(br.top(), br.left()))
        br.setRight(max(br.right(), br.bottom()))
        br.setBottom(max(br.right(), br.bottom()))
        return QtCore.QRectF(br)


class partition_tab(TabBase):

    def __init__(self, title='Partition'):
        super().__init__(title)

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def initialize(self, Network_UI):
        self.partition_tab = Network_UI.add_tab(title=self.title)

        def on_click(event):
            for sg in event.currentItem.sub_sgs:
                sg.selected=sg.dst_position_rect.contains(event.pos().x(), event.pos().y())

        self.draw_items = {}
        self.plots = {}
        for transmitter in Network_UI.transmitters:
            self.plots[transmitter] = Network_UI.tab.add_plot(tooltip_message='Click on a block of the right group(selected group) to show the possible inputs to this block\r\nLeft: Source NeuronGroup\r\nRight: Destination NeuronGroup\r\n(Partitioning is used for speeding up synapse operations)')
            self.draw_items[transmitter] = DrawItem()
            self.draw_items[transmitter].mouseClickEvent = on_click
            self.plots[transmitter].addItem(self.draw_items[transmitter])


    def update(self, Network_UI):
        if self.partition_tab.isVisible():
            group=Network_UI.selected_neuron_group()
            for transmitter in Network_UI.transmitters:
                self.draw_items[transmitter].update_pic(group.synapses(afferent, transmitter),group)
                self.plots[transmitter].update()