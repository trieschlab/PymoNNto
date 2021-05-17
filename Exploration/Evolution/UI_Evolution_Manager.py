from PymoNNto.Exploration.UI_Base import *
from PymoNNto.Exploration.StorageManager.StorageManager import *
from PymoNNto.Exploration.Evolution.SSH_Functions import *
from PymoNNto.Exploration.Evolution.EvolutionPlots import *
from multiprocessing import Process, Queue, Pipe
import shutil

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

def evolution_thread_worker(name, conn):
    print('local thread started')
    try:
        dir = os.getcwd()
        os.chdir(get_epc_folder()+'/'+name)

        system_str = sys.platform
        if 'darwin' in system_str:#mac os
            os.system('python execute_evolution.py')#todo: test
        elif 'win' in system_str:#windows
            os.system('start /wait cmd /c python execute_evolution.py')
        else:
            os.system('gnome-terminal -x python execute_evolution.py')

        os.chdir(dir)

        conn.send('execution finished')
    except:
        conn.send('thread error')
    conn.send('idle')


class UI_Evolution_Manager(UI_Base):

    def __init__(self):
        super().__init__(None, label='Evolution Monitor', create_sidebar=True)

        self.tabs.currentChanged.connect(self.On_Tab_Changed)

        ssm = SimpleStorageManager(get_epc_folder()+'/')
        servers = eval(ssm.load_param('servers', default="[]"))#['local', 'ssh vieth@poppy.fias.uni-frankfurt.de', 'ssh marius@hey3kmuagjunsk2b.myfritz.net', '+']
        self.listwidget2 = QListWidget()
        self.listwidget2.addItems(['+', 'local']+servers)
        self.listwidget2.currentItemChanged.connect(self.on_server_select)
        self.Add_element(self.listwidget2, stretch=10.0, sidebar=True)

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

        self.add_btn = self.Add_element(QPushButton('Add'), sidebar=True, stretch=1.0)
        self.add_btn.clicked.connect(self.on_add_click)

        for dir in os.listdir(get_epc_folder()):
            if os.path.isdir(get_epc_folder()+'/'+dir):
                self.add_tab(dir)

    def set_text(self, ssm, edit, text):
        data = ssm.load_param(text, default='', return_string=True)
        if data is not None and data != '':
            edit.setText(data)

    def On_Tab_Changed(self, i):
        if hasattr(self.tabs.currentWidget(), 'ssm'):
            ssm = self.tabs.currentWidget().ssm
            self.set_text(ssm, self.evo_name_edit, 'name')
            self.set_text(ssm, self.slave_file_edit, 'slave_file')
            self.set_text(ssm, self.inactive_genome_info_edit, 'inactive_genome_info')
            self.set_text(ssm, self.thread_number_edit, 'thread_number')
            self.set_text(ssm, self.individual_count_edit, 'individual_count')
            self.set_text(ssm, self.mutation_edit, 'mutation')
            self.set_text(ssm, self.death_rate_edit, 'death_rate')
            self.set_text(ssm, self.start_genomes_edit, 'start_genomes')
            self.set_text(ssm, self.constraints_edit, 'constraints')


    def update_status(self, tab, name):
        if 'ssh ' in tab.server:
            if name in ssh_get_running(tab.server):
                tab.status_label.setText('<font color="green">running</font>')
                return True
            else:
                tab.status_label.setText('<font color="red">inactive</font>')
                return False

        if 'local' in tab.server:
            if tab.process is not None:
                if tab.parent_conn.poll():
                    msg = tab.parent_conn.recv()
                    tab.process.kill()
                    tab.process = None
                    tab.status_label.setText('<font color="red">inactive</font>')
                    return False
                else:
                    tab.status_label.setText('<font color="green">running</font>')
                    return True
            else:
                tab.status_label.setText('<font color="red">inactive</font>')
                return False

    def add_tab(self, name):

        folder = get_epc_folder()+'/'+name+'/'

        tab = self.Next_Tab(name, stretch=0.0)

        tab.status_label = self.Add_element(QLabel('Status'))

        tab.ssm = SimpleStorageManager(folder)
        tab.server = tab.ssm.load_param('server', default=None)

        tab.gene_keys = tab.ssm.load_param('gene_keys', default=None)
        if tab.gene_keys is not None:
            tab.gene_keys = eval(tab.gene_keys)#should return list like ['a', 'b', 'c', 'd', 'e']  todo:save on evo start

        def refresh():
            try:
                print('refresh')
                if tab.server is not None and 'ssh ' in tab.server:
                    user, host, password = split_ssh_user_host_password_string(tab.server)
                    print('get Data')
                    get_Data(name, user, host, password)
                if tab.gene_keys is not None:
                    print('update plot')
                    update_evolution_plot(self, tab, name, tab.gene_keys, data_folder=get_data_folder() + '/Evolution_Project_Clones/' + name + '/Data')
            except:
                print('no plot data found in', name)

            self.update_status(tab, name)

        refresh_btn = self.Add_element(QPushButton('refresh state'))
        refresh_btn.clicked.connect(refresh)

        tab.process = None

        def start_continue():
            if 'ssh ' in tab.server:
                if not self.update_status(tab, name):
                    ssh_execute_evo(tab.server, name)
                else:
                    print('thread already running')

            if 'local' in tab.server:
                if tab.process is None:
                    tab.parent_conn, child_conn = Pipe()
                    tab.process = Process(target=evolution_thread_worker, args=(name, child_conn))
                    tab.process.start()
                else:
                    print('thread already running')

            self.update_status(tab, name)

        start_evo_btn = self.Add_element(QPushButton('Start/Continue'))
        start_evo_btn.clicked.connect(start_continue)

        def stop():
            if 'ssh ' in tab.server:
                ssh_stop_evo(tab.server, name)
                self.update_status(tab, name)
            if 'local' in tab.server:
                if tab.process is not None:
                    print('Please close terminal manually')
                    tab.process.kill()
                    tab.process.terminate()
                    tab.process.close()
                    tab.process=None


        stop_btn = self.Add_element(QPushButton('stop evolution'))
        stop_btn.clicked.connect(stop)


        def remove():
            if 'ssh ' in tab.server:
                ssh_stop_evo(tab.server, name, remove_evo=True)

            if 'local' in tab.server:
                if tab.process is not None:
                    print('Please close terminal manually')
                    tab.process.kill()
                    tab.process.terminate()
                    tab.process.close()
                    tab.process=None

            shutil.rmtree(get_epc_folder() + '/' + name + '/')
            self.tabs.removeTab(self.tabs.currentIndex())

        remove_btn = self.Add_element(QPushButton('remove'))
        remove_btn.clicked.connect(remove)

        self.Add_element(QLabel(tab.server))

        self.Next_H_Block(stretch=10)

        add_evolution_plot_items(self, tab)

        tab.folder = get_epc_folder() + '/' + name + '/'

        self.update_status(tab, name)
        self.On_Tab_Changed(None)

    def on_server_select(self):
        server_str = self.listwidget2.currentItem().text()
        if server_str == '+':
            text, ok = QInputDialog.getText(self.main_window, 'Add...', 'Add computing device "ssh user@host" or "ssh user@host password"')
            if ok and text != '+':
                self.listwidget2.addItem(text)
                ssm = SimpleStorageManager(get_epc_folder()+'/')
                print(ssm.absolute_path)
                ssm.save_param('servers', eval(ssm.load_param('servers', default="[]"))+[text])

    def on_file_click(self):
        print(self.listwidget.currentItem().text())

    def on_add_click(self):
        name = self.evo_name_edit.text()
        if is_invalid_evo_name(name):
            print('invalid evolution name.\r\n For savety reasons some names and characters are forbidden to avoid the accidental removal of files or folders')
        else:
            item = self.listwidget2.currentItem()
            if item is None:
                print('please select a server first')
            else:
                server_str = item.text()
                if os.path.exists(get_data_folder()+'/Evolution_Project_Clones/'+name):
                    print('evolution folder already exists')
                else:

                    self.copy_project(name, server_str)

                    folder = get_epc_folder()+'/'+name+'/'
                    ssm = SimpleStorageManager(folder)
                    ssm.save_param('server', server_str)

                    ssm.save_param('name', name)
                    ssm.save_param('slave_file', self.slave_file_edit.text())
                    ssm.save_param('inactive_genome_info', self.inactive_genome_info_edit.text())
                    ssm.save_param('thread_number', self.thread_number_edit.text())
                    ssm.save_param('individual_count', self.individual_count_edit.text())
                    ssm.save_param('mutation', self.mutation_edit.text())
                    ssm.save_param('death_rate', self.death_rate_edit.text())
                    ssm.save_param('start_genomes', self.start_genomes_edit.text())
                    ssm.save_param('constraints', self.constraints_edit.text())

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
                    exec_file = exec_file.replace('#start_genomes#', self.start_genomes_edit.text())
                    exec_file = exec_file.replace('#constraints#', self.constraints_edit.text())

                    evo_file = folder + 'execute_evolution.py'

                    md_file = open(folder + 'execute_evolution.py', "w")
                    md_file.write(exec_file)
                    md_file.close()

                    print('saving evolution config...')

                    gene_keys = list(eval(self.start_genomes_edit.text())[0].keys())
                    ssm.save_param('gene_keys', gene_keys)

                    if 'ssh' in server_str:
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


if __name__ == '__main__':
    UI_Evolution_Manager().show()

