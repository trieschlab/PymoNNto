from PymoNNto.Exploration.Network_UI.TabBase import *

class character_activation_tab(TabBase):

    def __init__(self, title='char'):
        super().__init__(title)
        self.title = title

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def initialize(self, Network_UI):
        if Network_UI.network['grammar_act', 0] is not None:
            self.reconstruction_tab = Network_UI.Next_Tab(self.title)


            self.source=Network_UI.network['grammar_act', 0]

            _, self.plt = Network_UI.Add_plot_curve(title='Character activations', return_plot=True, number_of_curves=0, x_label='t (iterations)', y_label='Network average ')

            self.max_char_scatter = pg.ScatterPlotItem(pen=(100,100,100), brush=(100,100,100))
            self.max_char_scatter.activity_data = []

            self.char_scatter_plots=[]
            for i in range(len(self.source.alphabet)):
                symbol = QPainterPath()
                # symbol.addEllipse(QtCore.QRectF(-0.5, -0.5, 1, 1))

                font = QFont()
                #font.setStyleHint(QFont.Helvetica)
                font.setPointSize(1)
                char=self.source.index_to_char(i)
                if char==' ':
                    char='_'
                symbol.addText(-0.5, 0.2, font, char)

                color=set(np.random.rand(3)*255)
                self.char_scatter = pg.ScatterPlotItem(pen=color, brush=color, symbol=symbol)
                self.plt.addItem(self.char_scatter)
                self.char_scatter_plots.append(self.char_scatter)
                self.char_scatter.activity_data = []

            #self.data = np.zeros((len(source.alphabet),1))

            #self.timesteps=100


    def update(self, Network_UI):
        if Network_UI.network['grammar_act', 0] is not None and self.reconstruction_tab.isVisible():
            group=Network_UI.network[Network_UI.neuron_select_group, 0]


            if hasattr(group, 'Input_Weights') and hasattr(group, 'output'):
                activation = group.Input_Weights.transpose().dot(group.output)

                self.max_char_scatter.activity_data.append(np.max(activation))
                if len(self.max_char_scatter.activity_data) > 50:
                    self.max_char_scatter.activity_data = self.max_char_scatter.activity_data[1:]

                iterations = group['n.iteration', 0, 'np'][-len(self.max_char_scatter.activity_data):]
                self.max_char_scatter.setData(iterations, self.max_char_scatter.activity_data, size=50)

                for i, char_scatter in enumerate(self.char_scatter_plots):
                    char_scatter.activity_data.append(activation[i])
                    if len(char_scatter.activity_data)>50:
                        char_scatter.activity_data=char_scatter.activity_data[1:]


                    char_scatter.setData(iterations, char_scatter.activity_data, size=50)#list(range(len(char_scatter.activity_data)))



                #if len(neuron_data.shape) > 1:
                #    neuron_data = neuron_data[:, Network_UI.neuron_select_id]
                #self.neuron_var_curves[var].setData(iterations, neuron_data)

                #self.char_Act_plots.setData(self.data)