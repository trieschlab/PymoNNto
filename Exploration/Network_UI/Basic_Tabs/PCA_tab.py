from PymoNNto.Exploration.Network_UI.TabBase import *
from PymoNNto.Exploration.Analysis.PCA import *

class PCA_tab(TabBase):

    def __init__(self, parameter='output', title='PCA', timesteps=1000):
        super().__init__(title)
        self.parameter = parameter
        self.timesteps = timesteps

    def add_recorder_variables(self, neuron_group, Network_UI):
        if hasattr(neuron_group, self.parameter):
            Network_UI.add_recording_variable(neuron_group, 'n.'+self.parameter, timesteps=self.timesteps)

    def initialize(self, Network_UI):
        self.pca_tab = Network_UI.Next_Tab(self.title)

        self.pca_curve = Network_UI.Add_plot_curve('PCA singular values', colors=[(0, 0, 0)], legend=False, x_label='singular value', y_label='')

        self.evr_curve = Network_UI.Add_plot_curve('PCA explained variance ratio', colors=[(0, 0, 0)], legend=False, x_label='features', y_label='% variance explained')

        Network_UI.Next_H_Block()

        self.singular_value_count=5

        self.singular_value_histories = [[] for i in range(self.singular_value_count)]
        self.singular_value_iterations = []

        self.sv_curves = Network_UI.Add_plot_curve(str(self.singular_value_count)+' biggest singular values', number_of_curves=self.singular_value_count, legend=False,x_label='singular value', y_label='')


    def update(self, Network_UI):
        if self.pca_tab.isVisible() and Network_UI.network.iteration%10==0:
            if len(Network_UI.network[Network_UI.neuron_select_group]) >= 0:
                group=Network_UI.network[Network_UI.neuron_select_group, 0]

                try:
                #if hasattr(group, self.parameter):

                    act = group['n.'+self.parameter, 0, 'np'][-self.timesteps:]
                    try :
                        pca = get_PCA(act, 100)
                        svs = pca.singular_values_
                        evr = pca.explained_variance_ratio_
                        if len(svs) >= self.singular_value_count:
                            self.singular_value_iterations.append(Network_UI.network.iteration)
                            for i in range(self.singular_value_count):
                                self.singular_value_histories[i].append(svs[i])
                                self.sv_curves[i].setData(self.singular_value_iterations, self.singular_value_histories[i])

                            self.pca_curve.setData(svs)
                            self.evr_curve.setData(np.cumsum(np.round(evr, decimals=3)*100))
                    except:
                        print('not enough timesteps for PCA. waiting...')

                except:
                    print(self.parameter, "cannot be evaluated")

