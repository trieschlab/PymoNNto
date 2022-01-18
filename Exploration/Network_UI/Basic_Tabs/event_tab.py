from PymoNNto.Exploration.Network_UI.TabBase import *

class event_tab(TabBase):

    def __init__(self, title='Events'):
        super().__init__(title)


    def initialize(self, Network_UI):
        self.event_tab = Network_UI.Next_Tab(self.title)

        _, self.plot = Network_UI.Add_plot_curve('Events', x_label='t (iterations)', y_label='events', number_of_curves=0, return_plot=True)

        self.current_pos = pg.PlotCurveItem([0, 0], [0, 0], pen=(100,100,100,255))
        self.plot.addItem(self.current_pos)

        self.plot.hideAxis('left')

        self.event_count = 0
        self.label_x_positions = []


    def update(self, Network_UI):
        if self.event_tab.isVisible():

            self.current_pos.setData([0, Network_UI.network.iteration], [0, 0])

            #update_plot
            for i,e in enumerate(Network_UI.event_list):
                if i>self.event_count:

                    if e.start_t!=e.end_t:
                        curve = pg.PlotCurveItem([e.start_t, e.end_t], [0, 0], fillLevel=10, brush=(30, 30, 30, 30), pen=None)
                        self.plot.addItem(curve)
                    else:
                        ypos = 2
                        for xp in self.label_x_positions:
                            if np.abs(e.start_t-xp)<30:
                                ypos += 0.5

                        if '(False)' in e.tag:
                            line = pg.InfiniteLine(pos=e.start_t, angle=90, pen=(100, 0, 0, 100), span=(0, 0.1))
                        elif '(True)' in e.tag:
                            line = pg.InfiniteLine(pos=e.start_t, angle=90, pen=(0, 100, 0, 100), span=(0, 0.1))
                        else:
                            line = pg.InfiniteLine(pos=e.start_t, angle=90, pen=(0, 0, 100, 100), span=(0, 0.1))

                        self.plot.addItem(line)

                        text = pg.TextItem(text=e.tag.replace('(False)', '(OFF)').replace('(True)', '(ON)'), anchor=(0.5, 0))
                        text.setPos(e.start_t, ypos)
                        self.plot.addItem(text)

                        self.label_x_positions.append(e.start_t)


                    self.event_count+=1


