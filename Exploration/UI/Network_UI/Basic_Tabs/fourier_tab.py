from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np

import scipy.fftpack

#import matplotlib.pyplot as plt

class fourier_tab():

    def __init__(self, parameter, title='fourier', timesteps=1000):
        self.title = title
        self.parameter = parameter
        self.timesteps=timesteps

    def add_recorder_variables(self, neuron_group, Network_UI):
        if hasattr(neuron_group, self.parameter):
            Network_UI.add_recording_variable(neuron_group, 'np.mean(n.'+self.parameter+')', timesteps=self.timesteps)

    def initialize(self, Network_UI):
        self.fourier_tab = Network_UI.Next_Tab(self.title)

        curves, exc_plt = Network_UI.Add_plot_curve('Selected Group Frequencies', colors=[(0, 0, 0)], legend=False, number_of_curves=6, return_plot=True, x_label='Frequency [Hz]', y_label='Amplitude')

        self.exc_fft_curve, self.exc_alpha, self.exc_beta, self.exc_theta, self.exc_delta, self.exc_gamma = curves

        self.exc_fft_curve.setData([0, 0], [0, 0.1])

        text = pg.TextItem(text='Delta', anchor=(0.5, 0))
        text.setPos(2, 0)
        exc_plt.addItem(text)

        text = pg.TextItem(text='Theta', anchor=(0.5, 0))
        text.setPos(6, 0)
        exc_plt.addItem(text)

        text = pg.TextItem(text='Alpha', anchor=(0.5, 0))
        text.setPos(11, 0)
        exc_plt.addItem(text)

        text = pg.TextItem(text='Beta', anchor=(0.5, 0))
        text.setPos(22, 0)
        exc_plt.addItem(text)

        text = pg.TextItem(text='Gamma', anchor=(0, 0))
        text.setPos(30, 0)
        exc_plt.addItem(text)

        '''
        Network_UI.Next_H_Block()

        curves, inh_plt = Network_UI.Add_plot_curve('Inhibitory', colors=[(255, 0, 0)], legend=False, number_of_curves=6, return_plot=True, x_label='Frequency [Hz]', y_label='Amplitude')

        self.inh_fft_curve, self.inh_alpha, self.inh_beta, self.inh_theta, self.inh_delta, self.inh_gamma = curves

        self.inh_fft_curve.setData([0, 0], [0, 0.1])

        text = pg.TextItem(text='Delta', anchor=(0.5, 0))
        text.setPos(2, 0)
        inh_plt.addItem(text)

        text = pg.TextItem(text='Theta', anchor=(0.5, 0))
        text.setPos(6, 0)
        inh_plt.addItem(text)

        text = pg.TextItem(text='Alpha', anchor=(0.5, 0))
        text.setPos(11, 0)
        inh_plt.addItem(text)

        text = pg.TextItem(text='Beta', anchor=(0.5, 0))
        text.setPos(22, 0)
        inh_plt.addItem(text)

        text = pg.TextItem(text='Gamma', anchor=(0, 0))
        text.setPos(30, 0)
        inh_plt.addItem(text)
        '''
        Network_UI.Next_H_Block()

        #Network_UI.Next_H_Block()

        Network_UI.Add_element(QLabel('Min:'))

        self.cut_slider = QSlider(1)
        self.cut_slider.setMinimum(0)
        self.cut_slider.setMaximum(10)
        self.cut_slider.setSliderPosition(1)
        Network_UI.Add_element(self.cut_slider)

        Network_UI.Next_H_Block()

        self.mspc_label=QLabel('ms/cycle:')
        Network_UI.Add_element(self.mspc_label)

        self.ms_per_cycle_slider = QSlider(1)
        self.ms_per_cycle_slider.setMinimum(1)
        self.ms_per_cycle_slider.setMaximum(100)
        self.ms_per_cycle_slider.setSliderPosition(10)
        Network_UI.Add_element(self.ms_per_cycle_slider)

        Network_UI.Next_H_Block()

        Network_UI.Add_element(QLabel('Smoothing:'))

        self.smooth_slider = QSlider(1)
        self.smooth_slider.setMinimum(0)
        self.smooth_slider.setMaximum(50)
        self.smooth_slider.setSliderPosition(0)
        Network_UI.Add_element(self.smooth_slider)

        #self.fouriers=[]

    def smooth(self, data):
        smoothed = data.copy()
        if len(data) > 1:
            for _ in range(int(self.smooth_slider.sliderPosition())):
                for i in range(len(data)):
                    if i == 0:
                        smoothed[i] = (smoothed[i] + smoothed[i + 1] + data[i]) / 3.0
                    elif i == len(data) - 1:
                        smoothed[i] = (smoothed[i] + smoothed[i - 1] + data[i]) / 3.0
                    else:
                        smoothed[i] = (smoothed[i] + smoothed[i - 1] + smoothed[i + 1]) / 3.0
        return smoothed

    def update(self, Network_UI):
        if self.fourier_tab.isVisible():
            if len(Network_UI.network[Network_UI.neuron_select_group]) >= 0:
                group=Network_UI.network[Network_UI.neuron_select_group, 0]

                if hasattr(group, 'output'):

                    cut = int(self.cut_slider.sliderPosition())
                    ms_per_cycle = int(self.ms_per_cycle_slider.sliderPosition())
                    self.mspc_label.setText('ms/cycle: {}'.format(ms_per_cycle))

                    # for name, min_f, max_f, color in [('alpha',8,13,'green'),('alpha',8,13,'green')]

                    # c2 = plt.plot([2, 1, 4, 3], pen='g', fillLevel=0, fillBrush=(255, 255, 255, 30), name='green plot')
                    # c3 = plt.addLine(y=4, pen='y')

                    #rec = group['rec_'+str(self.timesteps), 0]
                    #rec = Network_UI.rec(group, self.timesteps)
                    exc_act = group['np.mean(n.output)', 0, 'np'][-self.timesteps:]
                    N = len(exc_act)
                    T = ms_per_cycle / 1000
                    yf = scipy.fftpack.fft(exc_act)
                    xf = np.linspace(int(1.0 - N / 1000), int(1.0 / (2.0 * T)), int(N / 2))[cut:]
                    real = (2.0 / N * np.abs(yf[:N // 2]))[cut:]
                    self.exc_fft_curve.setData(xf, self.smooth(real))

                    # if len(exc_act)==1000:
                    #    self.fouriers.append(real)

                    # if Network_UI.network.iteration==2000:
                    #    plt.imshow(np.array(self.fouriers).transpose())
                    #    plt.show()

                    max_y = np.max(real) + 0.001
                    max_x = np.max(xf)

                    self.exc_delta.setData([0.1, 3.9], [0, 0], fillLevel=max_y, brush=(50, 250, 50, 50), pen=None)
                    self.exc_theta.setData([min(max_x, 4), min(max_x, 7.9)], [0, 0], fillLevel=max_y, brush=(100, 200, 50, 50), pen=None)
                    self.exc_alpha.setData([min(max_x, 8), min(max_x, 13.9)], [0, 0], fillLevel=max_y, brush=(150, 150, 50, 50), pen=None)
                    self.exc_beta.setData([min(max_x, 14), min(max_x, 29.9)], [0, 0], fillLevel=max_y, brush=(200, 100, 50, 50), pen=None)
                    self.exc_gamma.setData([min(max_x, 30), min(max_x, 100)], [0, 0], fillLevel=max_y, brush=(250, 50, 50, 50), pen=None)

                '''
                if len(Network_UI.network[Network_UI.inh_group_name]) > 0:
                    inh_act = Network_UI.network[Network_UI.inh_group_name, 0]['np.mean(n.output)', 0, 'np'][-1000:]
                    N = len(inh_act)
                    T = ms_per_cycle / 1000
                    yf = scipy.fftpack.fft(inh_act)
                    xf = np.linspace(1.0-N/1000, 1.0 / (2.0 * T), N / 2)
                    real = (2.0 / N * np.abs(yf[:N // 2]))[cut:]
                    self.inh_fft_curve.setData(xf[cut:], self.smooth(real))

                    max_y = np.max(real)+0.001
                    max_x = np.max(xf)

                    self.inh_delta.setData([0.1, 3.9], [0, 0], fillLevel=max_y, brush=(50, 250, 50, 50), pen=None)
                    self.inh_theta.setData([min(max_x, 4), min(max_x, 7.9)], [0, 0], fillLevel=max_y, brush=(100, 200, 50, 50), pen=None)
                    self.inh_alpha.setData([min(max_x, 8), min(max_x, 13.9)], [0, 0], fillLevel=max_y, brush=(150, 150, 50, 50), pen=None)
                    self.inh_beta.setData([min(max_x, 14), min(max_x, 29.9)], [0, 0], fillLevel=max_y, brush=(200, 100, 50, 50), pen=None)
                    self.inh_gamma.setData([min(max_x, 30), min(max_x, 100)], [0, 0], fillLevel=max_y, brush=(250, 50, 50, 50), pen=None)
                '''

