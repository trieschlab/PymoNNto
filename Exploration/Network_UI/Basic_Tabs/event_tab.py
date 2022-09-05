from PymoNNto.Exploration.Network_UI.TabBase import *

class event_tab(TabBase):

    def __init__(self, title='Events'):
        super().__init__(title)


    def initialize(self, Network_UI):
        self.event_tab = Network_UI.add_tab(title=self.title)

        self.plot = Network_UI.tab.add_plot(title='Events', x_label='t (iterations)', y_label='events')

        self.current_pos = pg.PlotCurveItem([0, 0], [0, 0], pen=(100,100,100,255))
        self.plot.addItem(self.current_pos)

        self.plot.hideAxis('left')

        self.event_count = 0
        self.label_x_positions = []

        self.ypos = 2.0


    def update(self, Network_UI):
        if self.event_tab.isVisible():

            self.current_pos.setData([0, Network_UI.network.iteration], [0, 0])

            #update_plot
            for i,e in enumerate(Network_UI.event_list):
                if i>self.event_count:

                    if e.start_t!=e.end_t:
                        curve = pg.PlotCurveItem([e.start_t, e.end_t], [0, 0], fillLevel=10, brush=(30, 30, 30, 30), pen=(30, 30, 30, 30))
                        self.plot.addItem(curve)
                    else:

                        if '(False)' in e.tag:
                            line = pg.InfiniteLine(pos=e.start_t, angle=90, pen=(100, 0, 0, 100), span=(0, 0.1))
                        elif '(True)' in e.tag:
                            line = pg.InfiniteLine(pos=e.start_t, angle=90, pen=(0, 100, 0, 100), span=(0, 0.1))
                        else:
                            line = pg.InfiniteLine(pos=e.start_t, angle=90, pen=(0, 0, 100, 100), span=(0, 0.1))


                        self.plot.addItem(line)

                        text = pg.TextItem(text=e.tag.replace('(False)', '(OFF)').replace('(True)', '(ON)'), anchor=(0.5, 0))
                        text.setPos(e.start_t, self.ypos)
                        self.ypos += 0.5
                        if self.ypos > 10.0:
                            self.ypos = 2.0
                        self.plot.addItem(text)

                        self.label_x_positions.append(e.start_t)


                    self.event_count+=1


