from PymoNNto.Exploration.UI_Base import *
from PymoNNto.Exploration.StorageManager.StorageManager import *
from PymoNNto.Exploration.Evolution.SSH_Functions import *
from PymoNNto.Exploration.Evolution.EvolutionPlots import *
from multiprocessing import Process, Queue, Pipe
import shutil
import os

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

def evolution_thread_worker(name, folder, conn):
    print('local thread started')
    try:
        dir = os.getcwd()
        os.chdir(get_epc_folder(folder)+'/'+name)
        print('move to', get_epc_folder(folder)+'/'+name)

        system_str = sys.platform
        if 'darwin' in system_str:#mac os
            os.system('python3 execute.py')
        elif 'win' in system_str:#windows
            os.system('start /wait cmd /c python3 execute.py')
        else:
            os.system('gnome-terminal -x python3 execute.py')

        os.chdir(dir)

        conn.send('execution finished')
    except:
        conn.send('thread error')
    conn.send('idle')


def copy_project(evo_name, device_str, folder):
    if device_str == 'local':
        clone_project(evo_name, folder)

    if 'ssh' in device_str:
        user, host, password = split_ssh_user_host_password_string(device_str)
        if user is not None and host is not None:
            transfer_project(evo_name, user, host, password)

        Data_Folder = get_data_folder()
        if Data_Folder != './Data':
            epc_folder = Data_Folder + '/'+folder
            create_folder_if_not_exist(epc_folder)
            run_folder = epc_folder + '/' + evo_name
            create_folder_if_not_exist(run_folder)


class Execution_Manager_UI_Base(UI_Base):

    def add_ui_elements(self, left_vertical_layout, right_vertical_layout):
        return

    def On_Tab_Changed(self, i):
        return

    def get_help_txt(self):
        return '''...
        '''

    def create_execution_file(self, name, folder, file):
        return False


    def save_configuration(self,ssm):#SimpleStorageManager
        return


    def valid_configuration(self):
        return True

    def add_additional_tab_elements(self, tab, name):
        return

    def get_folder(self):
        return 'Execution_Project_Clones'

    def get_title(self):
        return 'Execute and Transfer'

    def __init__(self):
        super().__init__(title=self.get_title(), create_sidebar=True)

        self.folder = self.get_folder()

        self.tabs.currentChanged.connect(self.On_Tab_Changed)


        #self.Add_element(QLabel('Task name:'), sidebar = True, stretch=1)
        #self.task_name_edit = self.Add_element(QLineEdit('task_name'), sidebar = True, stretch=1)

        #remove...
        horizontal_layout = QHBoxLayout()
        self.sidebar.get_layout().addLayout(horizontal_layout)

        left_vertical_layout = QVBoxLayout()
        horizontal_layout.addLayout(left_vertical_layout)
        left_vertical_layout.addWidget(QLabel('Task name'))
        left_vertical_layout.addWidget(QLabel('Device'))


        self.task_name_edit = QLineEdit('task_name')
        right_vertical_layout = QVBoxLayout()
        horizontal_layout.addLayout(right_vertical_layout)
        right_vertical_layout.addWidget(self.task_name_edit)

        #self.Add_element(QLabel('Device:'), sidebar = True, stretch=1)
        ssm = SimpleStorageManager(get_epc_folder() + '/')
        servers = eval(ssm.load_param('servers', default="[]"))
        self.listwidget2 = QComboBox()#self.Add_element(, sidebar=True, stretch=1)

        #self.listwidget2.SizeAdjustPolicy(3)

        self.listwidget2.addItems(['local'] + servers)#'+'
        #self.listwidget2.currentItemChanged.connect(self.on_server_select)

        server_horizontal_layout = QHBoxLayout()
        server_horizontal_layout.addWidget(self.listwidget2, stretch=10)

        add_btn = QPushButton("+")
        add_btn.clicked.connect(self.on_server_add)
        add_btn.setMaximumWidth(30)
        server_horizontal_layout.addWidget(add_btn, stretch=0)

        del_btn = QPushButton("-")
        del_btn.clicked.connect(self.on_server_delete)
        del_btn.setMaximumWidth(30)
        server_horizontal_layout.addWidget(del_btn, stretch=0)

        right_vertical_layout.addLayout(server_horizontal_layout)



        #self.Add_element(self.listwidget2, stretch=1, sidebar=True)

        self.add_ui_elements(left_vertical_layout, right_vertical_layout)

        self.add_btn = self.sidebar.add_widget(QPushButton('Add'), stretch=1)
        #self.add_btn = self.Add_element(QPushButton('Add'), sidebar=True, stretch=1)
        self.add_btn.clicked.connect(self.on_add_click)


        def help(event):
            layout = QVBoxLayout()
            pte = QPlainTextEdit()
            pte.setPlainText(self.get_help_txt())
            pte.setReadOnly(True)
            layout.addWidget(pte)

            # self.layout.addWidget(message)
            # self.layout.addWidget(self.buttonBox)

            dlg = QDialog()
            dlg.setWindowTitle("Help")
            dlg.setLayout(layout)
            dlg.resize(1000, 700)
            dlg.exec()

        help_btn = self.sidebar.add_widget(QLabel('Click for help'), stretch=1)
        help_btn.setStyleSheet('color: gray')
        help_btn.setAlignment(Qt.AlignCenter)
        help_btn.mouseReleaseEvent = help

        def on_restore_click():
            if self.archive_list.currentItem() is not None:
                file = self.archive_list.currentItem().text()
                if '.zip' in file:
                    zfile = get_epc_folder(self.folder) + '/' + file
                    zip_file = zipfile.ZipFile(zfile, mode='r')
                    zip_file.extractall(path=get_epc_folder(self.folder) + '/' + file.replace('.zip', '')  + '/')
                    zip_file.close()

                    self.add_common_tab(file.replace('.zip', ''))

                    os.remove(zfile)
                    self.update_archive()

        def on_delete_click():
            if self.archive_list.currentItem() is not None:
                file = self.archive_list.currentItem().text()
                if '.zip' in file:
                    zfile = get_epc_folder(self.folder) + '/' + file
                    os.remove(zfile)
                    self.update_archive()

        self.add_tab('...', stretch=0)
        self.archive_list = self.tab.add_widget(QLabel('Archive:'))
        self.tab.add_row(stretch=100)
        self.archive_list = self.tab.add_widget(QListWidget())
        self.tab.add_row(stretch=0)
        restore_btn = self.tab.add_widget(QPushButton('restore'))
        restore_btn.clicked.connect(on_restore_click)

        delete_btn = self.tab.add_widget(QPushButton('delete'))
        delete_btn.clicked.connect(on_delete_click)

        self.update_archive()

        for dir in os.listdir(get_epc_folder(self.folder)):
            if os.path.isdir(get_epc_folder(self.folder) + '/' + dir):
                self.add_common_tab(dir)

    def update_archive(self):
        self.archive_list.clear()
        for dir in os.listdir(get_epc_folder(self.folder)):
            if not os.path.isdir(get_epc_folder(self.folder) + '/' + dir) and '.zip' in dir:
                self.archive_list.addItem(dir)

    def select_file(self):
        dialog = QFileDialog()
        dialog.setWindowTitle('Select evolvable file')
        dialog.setNameFilter('Python Files (*.py)')
        dialog.setDirectory(get_root_folder())#QtCore.QDir.currentPath()
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            file=str(dialog.selectedFiles()[0])
            if get_root_folder() in file:
                file=file.replace(get_root_folder()+'/','')
                self.slave_file_edit.setText(file)
            else:
                print('file not in project directory')
        else:
            print('no file selected')

    #def keyPressEvent(self, event):
    #    if event.key() in [Qt.Key_I]:
    #        tab = self.tabs.currentWidget()
    #        print(tab.clicked_id)
    #        smg = StorageManagerGroup(tab.name, data_folder=get_data_folder() + '/'+self.folder+'/' + tab.name + '/Data')
    #        smg.sort_by('generation')
    #        sm = smg.StorageManagerList[tab.clicked_id]
    #        file = sm.absolute_path + sm.config_file_name
    #        print(file)
    #        with open(file) as f:
    #            lines = f.readlines()

    #            layout = QVBoxLayout()
    #            pte = QPlainTextEdit()
    #            pte.setPlainText('\r\n'.join(lines))
    #            pte.setReadOnly(True)
    #            layout.addWidget(pte)
    #            dlg = QDialog()
    #            dlg.setWindowTitle("Info")
    #            dlg.setLayout(layout)
    #            dlg.resize(600, 400)
    #            dlg.exec()

    def set_text(self, ssm, edit, text):
        data = ssm.load_param(text, default='', return_string=True)
        if data is not None and data != '':
            edit.setText(data)

    def update_status(self, tab, name):

        if os.path.exists(tab.ssm.get_path()+'Data/error.txt'):
            tab.warning_label.setVisible(True)

            def show_error_msg(event):
                layout = QVBoxLayout()
                pte = QPlainTextEdit()
                pte.setPlainText(tab.ssm.load_str('Data/error'))
                pte.setReadOnly(True)
                layout.addWidget(pte)

                dlg = QDialog()
                dlg.setWindowTitle("Error")
                dlg.setLayout(layout)
                dlg.resize(1100, 540)
                dlg.exec()

            tab.warning_label.mouseReleaseEvent = show_error_msg

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

    def refresh_view(self, tab):
        return

    def add_common_tab(self, name):

        folder = get_epc_folder(self.folder) + '/' + name + '/'

        tab = self.add_tab(name, stretch=0) #self.Next_Tab(name, stretch=0)
        tab.name = name

        tab.ssm = SimpleStorageManager(folder)
        tab.server = tab.ssm.load_param('server', default=None)

        tab.gene_keys = tab.ssm.load_param('gene_keys', default=None)
        if tab.gene_keys is not None:
            tab.gene_keys = eval(tab.gene_keys)

        tab.process = None
        #tab.python_cmd = tab.ssm.load_param('python_cmd', default='python3')

        if tab.ssm.load_param('executable', default=None) is not None:###################################################################################################

            tab.warning_label = self.tab.add_widget(QLabel(u"\u26A0"))
            tab.warning_label.setVisible(False)

            tab.status_label = self.tab.add_widget(QLabel('Status'))

            def refresh():
                try:
                    print('refresh')
                    if tab.server is not None and 'ssh ' in tab.server:
                        user, host, password = split_ssh_user_host_password_string(tab.server)
                        print('get Data')
                        get_Data(name, user, host, password, self.folder)
                except:
                    print('no plot data found in', name)

                self.update_status(tab, name)
                self.refresh_view(tab)

            refresh_btn = self.tab.add_widget(QPushButton('refresh state'))
            refresh_btn.clicked.connect(refresh)

            def start_continue():
                if 'ssh ' in tab.server:
                    if not self.update_status(tab, name):
                        ssh_execute_evo(tab.server, name)  # python3
                    else:
                        print('thread already running')

                if 'local' in tab.server:
                    if tab.process is None:
                        tab.parent_conn, child_conn = Pipe()
                        tab.process = Process(target=evolution_thread_worker,
                                              args=(name, self.folder, child_conn))  # python
                        print('start', self.folder+'/'+name+'/execute.py')
                        tab.process.start()
                    else:
                        print('thread already running')

                self.update_status(tab, name)

            start_evo_btn = self.tab.add_widget(QPushButton('start/continue'))
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
                        tab.process = None

            stop_btn = self.tab.add_widget(QPushButton('stop evolution'))
            stop_btn.clicked.connect(stop)

        #############################################################################################################

        self.tab.add_row(stretch=0)

        self.tab.add_widget(QLabel(tab.server))

        def archive():
            if  tab.server is not None and 'ssh ' in tab.server:
                ssh_stop_evo(tab.server, name, remove_evo=False)

            if  tab.server is not None and 'local' in tab.server:
                if tab.process is not None:
                    print('Please close terminal manually')
                    tab.process.kill()
                    tab.process.terminate()
                    tab.process.close()
                    tab.process = None

            zipDir(get_epc_folder(self.folder) + '/' + name, get_epc_folder(self.folder) + '/' + name + '.zip')
            shutil.rmtree(get_epc_folder(self.folder) + '/' + name + '/')
            self.tabs.removeTab(self.tabs.currentIndex())

            self.update_archive()

        archive_btn = self.tab.add_widget(QPushButton('archive'))
        archive_btn.clicked.connect(archive)

        def remove():
            if tab.server is not None and 'ssh ' in tab.server:
                ssh_stop_evo(tab.server, name, remove_evo=True)

            if tab.server is not None and 'local' in tab.server:
                if tab.process is not None:
                    print('Please close terminal manually')
                    tab.process.kill()
                    tab.process.terminate()
                    tab.process.close()
                    tab.process = None

            shutil.rmtree(get_epc_folder(self.folder) + '/' + name + '/')
            self.tabs.removeTab(self.tabs.currentIndex())

        remove_btn = self.tab.add_widget(QPushButton('remove'))
        remove_btn.clicked.connect(remove)


        self.add_additional_tab_elements(tab, name)

        self.On_Tab_Changed(None)



        # TODO: remove
        #smg = StorageManagerGroup(tab.name, data_folder=get_data_folder() + '/' + self.folder + '/' + tab.name + '/Data')
        #params = smg.get_all_params()
        #if 'generation' not in params and 'gen' in params:
        #    for sm in smg.StorageManagerList:
        #        g = sm.load_param('gen')
        #        sm.save_param('generation', g)

    def on_server_delete(self):
        txt = self.listwidget2.currentText()
        if  txt!= 'local':
            self.listwidget2.removeItem(self.listwidget2.currentIndex())
            ssm = SimpleStorageManager(get_epc_folder(self.folder) + '/')
            #print(ssm.absolute_path)
            servers = eval(ssm.load_param('servers', default="[]"))
            servers.remove(txt)
            ssm.save_param('servers',  servers)


    def on_server_add(self):
        #server_str = self.listwidget2.currentItem().text()
        #if server_str == '+':
        text, ok = QInputDialog.getText(self.main_window, 'Add...', 'Add computing device "ssh user@host" or "ssh user@host password"')
        if ok:
            self.listwidget2.addItem(text)
            ssm = SimpleStorageManager(get_epc_folder(self.folder) + '/')
            print(ssm.absolute_path)
            ssm.save_param('servers', eval(ssm.load_param('servers', default="[]")) + [text])

    def on_file_click(self):
        print(self.listwidget.currentItem().text())

    def on_add_click(self):
        name = self.task_name_edit.text()
        if is_invalid_evo_name(name):
            print(
                'invalid evolution name.\r\n For savety reasons some names and characters are forbidden to avoid the accidental removal of files or folders')
        else:
            item = self.listwidget2.currentText()
            if item is None:
                print('please select a server first')
            else:
                server_str = item
                if os.path.exists(get_data_folder() + '/'+self.folder+'/' + name):
                    print('folder already exists: '+ get_data_folder() + '/'+self.folder+'/' + name)
                elif self.valid_configuration():

                    copy_project(name, server_str, self.folder)

                    folder = get_epc_folder(self.folder) + '/' + name + '/'

                    ssm = SimpleStorageManager(folder)
                    ssm.save_param('server', server_str)
                    ssm.save_param('name', name)

                    self.save_configuration(ssm)

                    evo_file = folder + 'execute.py'
                    if self.create_execution_file(name, folder, evo_file):
                        ssm.save_param('executable', 'True')

                    print('saving config...')

                    if 'ssh' in server_str:
                        user, host, password = split_ssh_user_host_password_string(server_str)
                        print('transfer execute.py to ' + host + '...')
                        ssh = get_ssh_connection(host, user, password)
                        scp = SCPClient(ssh.get_transport())
                        scp.put(evo_file, name + '/execute.py')
                        scp.close()
                        ssh.close()

                    print('adding tab...')
                    self.add_common_tab(name)

if __name__ == '__main__':
    Execution_Manager_UI_Base().show()