from PymoNNto.Exploration.Network_UI.TabBase import *

#from Testing.Common.Classifier_Helper import *

class sidebar_drumbeat_module(TabBase):

    def add_recorder_variables(self, neuron_group, Network_UI):
        if hasattr(neuron_group, 'pattern_index'):
            Network_UI.add_recording_variable(neuron_group, 'pattern_index', timesteps=100)

    def initialize(self, Network_UI):
        if len(Network_UI.network['drum_act'])>0:

            self.readout = None

            def learning_on_off(event):
                Network_UI.network.set_behaviors('STDP', self.stdp_cb.isChecked())

            network = Network_UI.network
            source = network['drum_act', 0]

            p = Network_UI.Add_plot(sidebar=True, title='Input')#,axisItems={'left': stringaxis})

            self.scatter = pg.ScatterPlotItem()
            p.showGrid(y=True)
            p.addItem(self.scatter)

            p.setYRange(-1,source.A+2, padding=0)

            self.n_notes_shown=20
            p.setXRange(-1,self.n_notes_shown+1)


    def update(self, Network_UI):
        if len(Network_UI.network['drum_act'])>0:

            network = Network_UI.network
            source = network['drum_act', 0]
            curr_output = np.array(network['pattern_index', 0][-self.n_notes_shown:])

            y=[]
            x=[]
            ts=0
            for i in range(curr_output.shape[0]):
                indices = np.nonzero(curr_output[i])[0]
                if len(indices)==0:
                    x.append(ts)
                    y.append(np.nan)
                else:
                    for j in indices:
                        x.append(ts)
                        y.append(j)
                ts+=1
            self.scatter.setData(x,y)

            if len(x) > 0:#self.n_notes_shown:
                self.scatter.setData(x,y)
                self.scatter.setSize(2)

        
