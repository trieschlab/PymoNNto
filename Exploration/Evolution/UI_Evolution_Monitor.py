from Exploration.UI_Base import *
from PymoNNto.Exploration.StorageManager.StorageManager import *
from Exploration.Evolution.SSH_Functions import *
from PymoNNto.Exploration.Evolution.EvolutionPlots import *

class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)


class UI_Evolution_Monitor(UI_Base):

    def __init__(self):
        super().__init__(None, label='Evolution Monitor', create_sidebar=True)

        self.listwidget2 = QListWidget()
        self.listwidget2.addItems(['local', 'ssh vieth@poppy.fias.uni-frankfurt.de', 'ssh marius@hey3kmuagjunsk2b.myfritz.net', '+'])
        self.listwidget2.currentItemChanged.connect(self.on_server_select)
        self.Add_element(self.listwidget2, stretch=10.0, sidebar=True)

        #self.Add_element(QLabel('New Evolution:'), sidebar=True, stretch=0.0)

        #self.Add_element(QLabel('Server:'), sidebar=True, stretch=0.0)
        #self.server_edit = self.Add_element(QLineEdit('local'), sidebar=True, stretch=0.0)

        #self.refresh_btn = self.Add_element(QPushButton('Refresh'), sidebar=True, stretch=1.0)
        #self.refresh_btn.clicked.connect(self.on_refresh_click)

        #self.evo_name_edit = self.Add_element(, sidebar=True, stretch=0.0)

        #self.listwidget = QListWidget()
        #self.listwidget.currentItemChanged.connect(self.on_file_click)
        #self.Add_element(self.listwidget, stretch=10.0, sidebar=True)
        #self.cb = QComboBox()
        #self.Add_element(self.cb, stretch=10.0, sidebar=True)

        horizontal_layout = QHBoxLayout()
        self.sidebar_current_vertical_layout.addLayout(horizontal_layout)

        vertical_layout = QVBoxLayout()
        horizontal_layout.addLayout(vertical_layout)
        vertical_layout.addWidget(QLabel('evo name'))
        vertical_layout.addWidget(QLabel('slave file'))
        vertical_layout.addWidget(QLabel('inactive info'))
        vertical_layout.addWidget(QLabel('thread number'))
        vertical_layout.addWidget(QLabel('individual count'))
        vertical_layout.addWidget(QLabel('mutation'))
        vertical_layout.addWidget(QLabel('death rate'))
        vertical_layout.addWidget(QLabel('start geneomes'))
        vertical_layout.addWidget(QLabel('constriants'))

        self.evo_name_edit = QLineEdit('evo_name')
        self.slave_file_edit = QLineEdit('Exploration/Evolution/test_slave.py')
        self.inactive_genome_info_edit = QLineEdit('{}')
        self.thread_number_edit = QLineEdit('4')
        self.individual_count_edit = QLineEdit('10')
        self.mutation_edit = QLineEdit('0.05')
        self.death_rate_edit = QLineEdit('0.5')
        self.start_genomes_edit = QLineEdit("[{'a':1,'b':2,'c':2,'d':2,'e':3}]")
        self.constraints_edit = QLineEdit("['a<b','b<=c']")


        vertical_layout = QVBoxLayout()
        horizontal_layout.addLayout(vertical_layout)
        vertical_layout.addWidget(self.evo_name_edit)
        vertical_layout.addWidget(self.slave_file_edit)
        vertical_layout.addWidget(self.inactive_genome_info_edit)
        vertical_layout.addWidget(self.thread_number_edit)
        vertical_layout.addWidget(self.individual_count_edit)
        vertical_layout.addWidget(self.mutation_edit)
        vertical_layout.addWidget(self.death_rate_edit)
        vertical_layout.addWidget(self.start_genomes_edit)
        vertical_layout.addWidget(self.constraints_edit)


        #self.current_H_block.addWidget(QVLine())


        self.add_btn = self.Add_element(QPushButton('Add'), sidebar=True, stretch=1.0)
        self.add_btn.clicked.connect(self.on_add_click)

        #self.copy_project('test', 'ssh user@host')
        #self.copy_project('test2', 'ssh user@host')
        #self.copy_project('test3', 'ssh user@host')

        for dir in os.listdir(get_epc_folder()):
            tab = self.add_tab(dir)

        #self.refresh_evolution_file()
        #self.reduced_layout = False
        #self.Next_H_Block(stretch=10)
        #self.Next_H_Block(stretch=0.0)
        #self.Add_element(QLabel('New Evolution_Old Name:'), stretch=0)



    def add_tab(self, name):

        folder = get_epc_folder()+'/'+name+'/'

        tab = self.Next_Tab(name, stretch=0.0)

        self.Add_element(QLabel('Status'))

        tab.ssm = SimpleStorageManager(folder)
        tab.server = tab.ssm.load_param('server', default=None)
        tab.gene_keys = tab.ssm.load_param('gene_keys', default=None)
        if tab.gene_keys is not None:
            tab.gene_keys=eval(tab.gene_keys)#should return list like ['a', 'b', 'c', 'd', 'e']  todo:save on evo start

        def refresh():
            try:
                if tab.server is not None and 'ssh ' in tab.server:
                    user, host, password = split_ssh_user_host_password_string(tab.server)
                    print('get Data')
                    get_Data(name, user, host, password)
                if tab.gene_keys is not None:
                    print('update plot')
                    update_evolution_plot(self, tab, name, tab.gene_keys, data_folder=get_data_folder() + '/Evolution_Project_Clones/' + name + '/Data')
            except:
                print('no plot data found in', name)
        refresh_btn = self.Add_element(QPushButton('refresh state'))
        refresh_btn.clicked.connect(refresh)


        #show_evo_file_btn = self.Add_element(QPushButton('show_evo_file_btn'))

        def start_continue():
            if 'ssh ' in tab.server:
                ssh_execute_evo(tab.server, name)

        start_evo_btn = self.Add_element(QPushButton('Start/Continue'))
        start_evo_btn.clicked.connect(start_continue)


        def stop():
            if 'ssh ' in tab.server:
                ssh_stop_evo(tab.server, name)


        stop_btn = self.Add_element(QPushButton('stop evolution'))
        stop_btn.clicked.connect(stop)

        #def remove():
        #    if 'ssh ' in tab.server:
        #        ssh_stop_evo(tab.server, name)
        #        #os.remove()

        #remove_btn = self.Add_element(QPushButton('remove'))
        #remove_btn.clicked.connect(remove)

        self.Add_element(QLabel(tab.server))

        #self.Next_H_Block(stretch=0)
        #self.Add_element(QLabel(''))

        #self.Next_H_Block(stretch=0)
        #self.Add_element(QHLine())

        #self.Next_H_Block(stretch=0)
        #self.Add_element(QLabel(''))

        #def remove():
        #    os.remove(folder)
        #remove_btn = self.Add_element(QPushButton('remove evolution'))
        #remove_btn.clicked.connect(remove)


        self.Next_H_Block(stretch=10)

        add_evolution_plot_items(self, tab)

        tab.folder = get_epc_folder() + '/' + name + '/'

        '''
            if tab.server is not None:

                #print('executing' + command)

                if 'ssh ' in tab.server:
                    user, host, password = split_ssh_user_host_password_string(tab.server)
                    ssh = get_ssh_connection(host, user, password)

                    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('python3 -c "import PymoNNto; print(PymoNNto.__file__)"')
                    response = get_response(ssh_stdout, ssh_stderr)
                    if len(response) > 0:
                        Remote_Evolution_Executer_Path = response[0].replace('__init__.py', 'Exploration/Evolution/Remote_Evolution_Executer.py')
                        print(Remote_Evolution_Executer_Path)


                        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
                        print(get_response(ssh_stdout, ssh_stderr))

                        #'cd ' + self.main_path + evo_name + '/Exploration/Evolution_Old/; screen -dmS ' + evo_name + ' sh; screen -S ' + evo_name + ' -X stuff "' + pexc + ' \r\n"'


                    ssh.close()

                if tab.server == 'local':
                    return
        '''









        #smg=StorageManagerGroup('my_test_evo', None, get_data_folder()+'/Evolution_Project_Clones/my_test_evo/Data')
        #for sm in smg.StorageManagerList:
        #    print(sm.folder_name)

    #def refresh_evolution_file(self):
    #    mainfolder = get_data_folder().replace('/Data', '/')
    #    for folder in os.walk(mainfolder):
    #        foldername = folder[0].replace('\\', '/')
    #        for file in os.listdir(foldername):
    #            if '.py' in file and not '.pyc' in file and not '__init__' in file and not 'UI_Evolution_Monitor' in file:
    #                filepath = foldername + '/' + file
    #                py_file = open(filepath, "r")
    #                py_text = py_file.read()
    #                py_file.close()
    #                if 'Evolution(' in py_text:
    #                    # filepath.replace(mainfolder,'')
    #                    self.listwidget.addItem(file)

    def on_server_select(self):
        server_str = self.listwidget2.currentItem().text()
        if server_str == '+':
            text, ok = QInputDialog.getText(self.main_window, 'Add...', 'Add computing device "ssh user@host" or "ssh user@host password"')
            if ok and text!='+':
                self.listwidget2.addItem(text)

    def on_file_click(self):
        print(self.listwidget.currentItem().text())

    def on_add_click(self):
        name = self.evo_name_edit.text()
        item = self.listwidget2.currentItem()
        if item is not None:
            server_str = item.text()

            self.copy_project(name, server_str)

            folder=get_epc_folder()+'/'+name+'/'
            ssm = SimpleStorageManager(folder)
            ssm.save_param('server', server_str)

            exec_file = """
from PymoNNto.Exploration.Evolution.Evolution import *
if __name__ == '__main__':
    evo = Evolution(name='#name#',
                slave_file='#slave_file#',
                individual_count=#individual_count#,
                mutation=#mutation#,
                death_rate=#death_rate#,
                constraints=#constraints#,
                inactive_genome_info=#inactive_genome_info#,
                start_genomes=#start_genomes#,
                devices={'multi_thread': #thread_number#}
                )

    if not evo.start(ui=False):
        evo.continue_evolution(ui=False)
"""

            print('generate execute_evolution.py...')
            exec_file = exec_file.replace('#name#', name)
            exec_file = exec_file.replace('#slave_file#', self.slave_file_edit.text())
            exec_file = exec_file.replace('#inactive_genome_info#', self.inactive_genome_info_edit.text())
            exec_file = exec_file.replace('#thread_number#', self.thread_number_edit.text())
            exec_file = exec_file.replace('#individual_count#', self.individual_count_edit.text())
            exec_file = exec_file.replace('#mutation#', self.mutation_edit.text())
            exec_file = exec_file.replace('#death_rate#', self.death_rate_edit.text())
            exec_file = exec_file.replace('#start_genomes#',self.start_genomes_edit.text())
            exec_file = exec_file.replace('#constraints#', self.constraints_edit.text())

            evo_file = folder + 'execute_evolution.py'

            md_file = open(folder + 'execute_evolution.py', "w")
            md_file.write(exec_file)
            md_file.close()

            print('saving evolution config...')

            gene_keys = list(eval(self.start_genomes_edit.text())[0].keys())
            ssm.save_param('gene_keys', gene_keys)

            user, host, password = split_ssh_user_host_password_string(server_str)
            print('transfer execute_evolution.py to ' + host + '...')
            ssh = get_ssh_connection(host, user, password)
            scp = SCPClient(ssh.get_transport())
            scp.put(evo_file, name + '/execute_evolution.py')
            scp.close()
            ssh.close()

            print('adding tab...')
            self.add_tab(name)

    def copy_project(self, evo_name, device_str):
        if device_str == 'local':
            clone_project(evo_name)

        if 'ssh' in device_str:
            user, host, password = split_ssh_user_host_password_string(device_str)
            if user is not None and host is not None:
                transfer_project(evo_name, user, host, password)

            Data_Folder = get_data_folder()
            if Data_Folder != './Data':
                epc_folder = Data_Folder + '/Evolution_Project_Clones'
                create_folder_if_not_exist(epc_folder)
                run_folder = epc_folder + '/' + evo_name
                create_folder_if_not_exist(run_folder)
                #description = run_folder + '/' + device_str
                #create_folder_if_not_exist(description)



    #def on_refresh_click(self):
    #    item=self.listwidget2.currentItem()
    #    if item is not None:
    #        server_str = item.text()
    #        if server_str!='+':
    #            print(server_str)

        #if server_str=='local':
            #dir=get_data_folder()+'/StorageManager/'
            #self.cb.addItems(os.listdir(dir))

        #if 'ssh' in server_str:
        #    user, host, password = split_ssh_user_host_password_string(server_str)

        #    ssh = get_ssh_connection(host, user, password)
        #    cmd = 'cd ' + name + '/' + root_folder + '; '
        #    cmd += 'python3 ' + slave_file + ' genome=' + get_gene_id(genome)
        #    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)

        #    results = get_response(ssh_stdout, ssh_stderr)

        #    ssh.close()




UI_Evolution_Monitor().show()

