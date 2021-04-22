from PymoNNto.Exploration.UI_Base import *
from PymoNNto.Exploration.StorageManager.StorageManager import *
from PymoNNto.Exploration.Evolution.EvolutionPlots import *



class UI_Single_Evolution_Monitor(UI_Base):

    def __init__(self, evolution):
        super().__init__(None, label='Evolution Monitor', create_sidebar=False)

        self.evolution = evolution

        self.main_tab = self.Next_Tab('Evolution performance', stretch=0.0)

        self.reduced_layout = False

        self.Next_H_Block(stretch=10)

        add_evolution_plot_items(self, self.main_tab)

        self.Next_H_Block(stretch=0.0)
        self.pause_cont_btn = self.Add_element(QPushButton('Pause'), stretch=0)
        self.pause_cont_btn.clicked.connect(self.on_pause_cont_click)

        #self.Add_element(QLabel('...'), stretch=0)

        self.last_generation = -1

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(40)

    def on_pause_cont_click(self):
        if self.timer.isActive():
            self.timer.stop()
            self.pause_cont_btn.setText('Start')
            print('stopped (only the main distribution timer is stopped but the remaining threads are still running to complete their current jobs)')
        else:
            self.timer.start(40)
            self.pause_cont_btn.setText('Pause')
            print('started')

    def on_timer(self):
        self.evolution.iteration()

    def update(self):
        if self.last_generation != self.evolution.Breed_And_Select.generation:
            update_evolution_plot(self, self.main_tab, self.evolution.name, self.evolution.gene_keys)
            self.last_generation = self.evolution.Breed_And_Select.generation
