import pyqtgraph as pg
from Testing.Common.Classifier_Helper import *


class sidebar_music_module():

    def add_recorder_variables(self, neuron_group, Network_UI):
        if hasattr(neuron_group, 'pattern_index'):
            Network_UI.add_recording_variable(neuron_group, 'n.pattern_index', timesteps=100)

    def initialize(self, Network_UI):
        if len(Network_UI.network['music_act'])>0:

            self.readout = None

            def learning_on_off(event):
                Network_UI.network.set_mechanisms(['STDP'], self.stdp_cb.isChecked())

            network = Network_UI.network
            source = network['music_act', 0]
            min_midi = min(filter(lambda x: x > 0, source.alphabet))
            max_midi = max(source.alphabet)

            stringaxis = pg.AxisItem(orientation='left')

            ticks = np.arange(24, 121, 12)
            ticks = ticks[np.where(np.logical_and(ticks>=min_midi, ticks<=max_midi))]
            ticks_strings= []
            for i in range(len(ticks)):
                ticks_strings.append(source.midi_index_to_notestring(ticks[i]))
            c_ticks = dict(zip(ticks,ticks_strings))
            stringaxis.setTicks([c_ticks.items()])

            p = Network_UI.Add_plot(sidebar=True, title='Input', axisItems={'left': stringaxis})

            self.scatter = pg.ScatterPlotItem()
            p.showGrid(y=True)
            p.addItem(self.scatter)

            p.setYRange(min_midi,max_midi, padding=0)
            self.n_notes_shown=20
            p.setXRange(-1,self.n_notes_shown+1)

            #image = pg.ImageItem(np.rot90(np.asarray(Image.open('midis_piano_cropped.png'))))
            #image.scale(0.05, 0.1)
            #p.addItem(image)

    
    def update(self, Network_UI):
        if len(Network_UI.network['music_act'])>0:

            network = Network_UI.network
            source = network['music_act', 0]
            curr_output = np.array(network['n.pattern_index', 0][-self.n_notes_shown:])

            if source.type=='poly':
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
                            y.append(source.alphabet[j])
                    ts+=1
                self.scatter.setData(x,y)

            elif source.type=='mono':
                midi_indices = np.empty(curr_output.shape)
            
                for i in range(len(curr_output)):
                    midi_indices[i] = source.alphabet[curr_output[i]]
                    if midi_indices[i] == -1:
                        midi_indices[i]=np.nan
                    
                x = np.arange(len(midi_indices))
                y = midi_indices

                #if len(midi_indices)>=self.n_notes_shown:
            if len(x) > 0:#self.n_notes_shown:
                self.scatter.setData(x,y)
                self.scatter.setSize(2)

            #current_corpus_index = source.current_index()
        
