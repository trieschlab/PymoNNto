import sys
sys.path.append('../../')

from Exploration.UI.UI_Base import *
from functools import partial
import Exploration.Evolution.Computing_Devices as comp_dev
import os

class EVO_UI(UI_Base):

    def refresh_status(self, evo_server):
        status='...'
        if evo_server.Evo_Select_Combo_Box.currentText() != '':
            evo_server.running_evo_list = evo_server.running_evos()

            if evo_server.Evo_Select_Combo_Box.currentText() in evo_server.running_evo_list:
                status = '<font color="green">running</font>'
            else:
                status = '<font color="red">stopped</font>'

            evo_server.status_label.setToolTip(str(evo_server.running_evo_list))

        evo_server.status_label.setText('Status: ' + status)
        evo_server.evo_name_edit.setText(evo_server.Evo_Select_Combo_Box.currentText())

    def plot_data(self, evo_server, data):
        evo_server.curve1.setData(data)

        # smoothing
        data2 = data.copy()
        if len(data) > 1:
            for _ in range(20):
                for i in range(len(data)):
                    if i == 0:
                        data2[i] = (data2[i] + data2[i + 1] + data[i]) / 3.0
                    elif i == len(data) - 1:
                        data2[i] = (data2[i] + data2[i - 1] + data[i]) / 3.0
                    else:
                        data2[i] = (data2[i] + data2[i - 1] + data2[i + 1]) / 3.0

        evo_server.curve2.setData(data2)

    def update_evo_list(self, evo_server):
        evo_list = evo_server.evolution_list()
        evo_server.Evo_Select_Combo_Box.clear()
        evo_server.Evo_Select_Combo_Box.addItems(evo_list)
        evo_server.Evo_Select_Combo_Box.setCurrentIndex(0)
        evo_server.evo_name_edit.setText(evo_server.Evo_Select_Combo_Box.currentText())
        self.refresh_status(evo_server)

    def __init__(self):
        super().__init__(None, label='EVO manager', create_sidebar=False)
        self.reduced_layout = False
        self.evo_servers = comp_dev.get_devices()

        for evo_server in self.evo_servers:
            evo_server.main_tab = self.Next_Tab(evo_server.name, stretch=0.0)

            def group_changed(evo_server):
                self.refresh_status(evo_server)
                evo_server.curve1.clear()
                evo_server.curve2.clear()#refresh...

            evo_server.Evo_Select_Combo_Box = QComboBox()
            self.Add_element(evo_server.Evo_Select_Combo_Box, stretch=4)
            evo_server.Evo_Select_Combo_Box.currentIndexChanged.connect(partial(group_changed, evo_server))

            evo_server.status_label = QLabel('Status: ...')
            self.Add_element(evo_server.status_label, stretch=4)

            def open_terminal(evo_server):
                evo_name = evo_server.Evo_Select_Combo_Box.currentText()
                if evo_name != '':
                    evo_server.open_terminal(evo_name)
                else:
                    print('no evolution selected')

            evo_server.open_terminal_btn = QPushButton('terminal', self.main_window)
            evo_server.open_terminal_btn.clicked.connect(partial(open_terminal, evo_server))
            self.Add_element(evo_server.open_terminal_btn, stretch=1)

            def refresh(evo_server):
                evo_name = evo_server.Evo_Select_Combo_Box.currentText()
                if evo_name != '':
                    data = evo_server.plot_data(evo_name)
                    self.plot_data(evo_server, data)
                else:
                    print('no evolution selected')
                self.refresh_status(evo_server)

            evo_server.refresh_btn = QPushButton('refresh plot', self.main_window)
            evo_server.refresh_btn.clicked.connect(partial(refresh, evo_server))
            self.Add_element(evo_server.refresh_btn, stretch=1)

            def stop(evo_server):
                evo_name = evo_server.Evo_Select_Combo_Box.currentText()
                if evo_name != '':
                    evo_server.terminate_screen(evo_name)
                else:
                    print('no evolution selected')
                self.refresh_status(evo_server)

            evo_server.stop_btn = QPushButton('Stop', self.main_window)
            evo_server.stop_btn.clicked.connect(partial(stop, evo_server))
            self.Add_element(evo_server.stop_btn, stretch=1)

            def remove(evo_server):
                evo_name = evo_server.Evo_Select_Combo_Box.currentText()
                if evo_name != '':
                    evo_server.terminate_screen(evo_name)
                    evo_server.remove_evo(evo_name)
                else:
                    print('no evolution selected')
                self.update_evo_list(evo_server)
                evo_server.curve1.clear()
                evo_server.curve2.clear()


            evo_server.remove_btn = QPushButton('Remove', self.main_window)
            evo_server.remove_btn.clicked.connect(partial(remove, evo_server))
            self.Add_element(evo_server.remove_btn, stretch=1)



            self.Next_H_Block(stretch=10)
            evo_server.curve1, evo_server.curve2 = self.Add_plot_curve('plot', number_of_curves=2)

            self.Next_H_Block(stretch=0.0)

            self.Add_element(QLabel('New Evolution Name:'), stretch=0)

            evo_server.evo_name_edit = QLineEdit('Evo_name')
            self.Add_element(evo_server.evo_name_edit, stretch=4)

            def add(evo_server):
                evo_name = evo_server.evo_name_edit.text()
                if evo_name != '' and evo_name != evo_server.Evo_Select_Combo_Box.currentText():
                    if evo_server.send_to_all_cb.isChecked():
                        for serv in self.evo_servers:
                            serv.transfer(evo_name)
                            self.update_evo_list(serv)
                    else:
                        evo_server.transfer(evo_name)
                        self.update_evo_list(evo_server)
                else:
                    print('please enter an evolution-name')

            evo_server.send_to_all_cb = QCheckBox('to all devices')
            self.Add_element(evo_server.send_to_all_cb, stretch=0)

            evo_server.add_btn = QPushButton('transfer to server', self.main_window)
            evo_server.add_btn.clicked.connect(partial(add, evo_server))
            self.Add_element(evo_server.add_btn, stretch=1)

            self.Next_H_Block(stretch=0.0)

            self.Add_element(QLabel('Execution file:'), stretch=0)
            evo_server.Class_Select_Combo_Box = QComboBox()

            files = []
            for r, d, f in os.walk('../../Testing'):
                rd = r.replace('../../', '').replace('\\', '.').replace('/', '.')
                for file in f:
                    if not 'Common' in rd and not 'Old' in rd and not '__pycache__' in rd:
                        files.append(rd+'.'+file.replace('.py', ''))
            print(files)

            evo_server.Class_Select_Combo_Box.addItems(files)#["Testing.SORN_Grammar.Experiment_PV_SOM", "Testing.SORN_GrammarExperiment_Hierarchical"]
            evo_server.Class_Select_Combo_Box.setCurrentIndex(0)
            self.Add_element(evo_server.Class_Select_Combo_Box, stretch=4)

            self.Add_element(QLabel('Genes:'), stretch=1)
            evo_server.evo_individuals_edit = QLineEdit('[0.95, 0.4, 0.1383, 0.1698, 0.1, 0.00015, 0.04, 0.2944, 0.0006, 0.5, 0.015, 0.2944, 0.1, 0.0001, 0.87038, 0.82099, 1.5, 0.08, 15.0]')
            self.Add_element(evo_server.evo_individuals_edit, stretch=28)

            self.Next_H_Block(stretch=0.0)

            self.Add_element(QLabel('Mutation rate:'), stretch=0)
            evo_server.mutation_edit = QLineEdit("0.05")
            self.Add_element(evo_server.mutation_edit, stretch=0)

            self.Add_element(QLabel('Ind_count:'), stretch=0)
            evo_server.ind_count_edit = QLineEdit("30")
            self.Add_element(evo_server.ind_count_edit, stretch=0)

            self.Add_element(QLabel('Threads:'), stretch=0)
            evo_server.thread_count_edit = QLineEdit("4")
            self.Add_element(evo_server.thread_count_edit, stretch=0)

            self.Add_element(QLabel('N_e:'), stretch=0)
            evo_server.N_e_edit = QLineEdit("900")
            self.Add_element(evo_server.N_e_edit, stretch=0)

            self.Add_element(QLabel('TS:'), stretch=0)
            evo_server.TS_edit = QLineEdit("[1]")
            self.Add_element(evo_server.TS_edit, stretch=0)

            evo_server.distributed_evo_cb = QCheckBox('distributed evolution')
            self.Add_element(evo_server.distributed_evo_cb, stretch=0)

            evo_server.execute_btn = QPushButton('execute', self.main_window)
            def execute(evo_server):
                evo_name = evo_server.Evo_Select_Combo_Box.currentText()
                if evo_name != '':
                    #evo_name = evo_server.evo_name_edit.text()
                    individuals = evo_server.evo_individuals_edit.text()
                    import_file = evo_server.Class_Select_Combo_Box.currentText()
                    mutation = evo_server.mutation_edit.text()
                    distributed = evo_server.distributed_evo_cb.isChecked()
                    thread_count = evo_server.thread_count_edit.text()
                    ind_count = evo_server.ind_count_edit.text()

                    N_e = evo_server.N_e_edit.text()
                    TS = evo_server.TS_edit.text()

                    evo_server.execute(evo_name, ['name='+evo_name, 'max_individual_count='+ind_count, 'thread_count='+thread_count, 'individuals='+individuals, 'import_file='+import_file, 'mutation='+str(mutation), 'distributed='+str(distributed), 'N_e='+N_e, 'TS='+TS])
                    self.update_evo_list(evo_server)
                else:
                    print('no evolution selected')

            evo_server.execute_btn.clicked.connect(partial(execute, evo_server))
            self.Add_element(evo_server.execute_btn, stretch=1)




            self.update_evo_list(evo_server)



EVO_UI().show()
