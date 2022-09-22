from PymoNNto.Exploration.Evolution.common_UI import *
from PymoNNto.Exploration.Evolution.communication import *

class UI_Evolution_Manager(Execution_Manager_UI_Base):

    def get_folder(self):
        return 'Evolution_Project_Clones'

    def get_title(self):
        return 'Evolution Monitor'

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

    def add_ui_elements(self, left_vertical_layout, right_vertical_layout):
        #horizontal_layout = QHBoxLayout()
        #self.sidebar_current_vertical_layout.addLayout(horizontal_layout)

        #left_vertical_layout = QVBoxLayout()
        #horizontal_layout.addLayout(left_vertical_layout)
        label = QLabel(u"\u24D8 " + "Slave file") #\u24BE
        label.setToolTip("path to python file which is supposed to be evolved (relative from root folder in which the Data folder is located)")
        left_vertical_layout.addWidget(label)

        label = QLabel(u"\u24D8 " + 'Thread number')
        label.setToolTip("number of worker threads")
        left_vertical_layout.addWidget(label)

        label = QLabel(u"\u24D8 " + 'Individual count')
        label.setToolTip("number of individuals in one generation")
        left_vertical_layout.addWidget(label)

        label = QLabel(u"\u24D8 " + 'Mutation')
        label.setToolTip("the parameter determines the mutation with: gene_new = normal(gene_old, clip(gene_old*mutation,0))")
        left_vertical_layout.addWidget(label)

        label = QLabel(u"\u24D8 " + 'Death rate')
        label.setToolTip("number of individuals with bad scores which are removed from each generation")
        left_vertical_layout.addWidget(label)

        #pc_label = QLabel(u"\u24D8 " + 'Python cmd')
        #pc_label.setToolTip("python command of the execution device (python or python3)")
        #left_vertical_layout.addWidget(pc_label)

        ii_label = QLabel(u"\u24D8 " + 'Inactive info')
        ii_label.setToolTip("additional genome that is passed to individuals but is not changed or optimized during the evolution run")
        left_vertical_layout.addWidget(ii_label)

        c_label = QLabel(u"\u24D8 " + 'Constriants')
        c_label.setToolTip("Example: ['a<b','b<=c'] if a b and c are genes")
        left_vertical_layout.addWidget(c_label)

        eo_label = QLabel(u"\u24D8 " + 'Evo options')
        eo_label.setToolTip("not used for now")
        left_vertical_layout.addWidget(eo_label)


        self.slave_file_edit = QLineEdit('Exploration/Evolution/example_slave.py')
        self.thread_number_edit = QLineEdit('4')
        #self.python_cmd_edit = QLineEdit("python3")
        #self.python_cmd_edit = QComboBox()
        #self.python_cmd_edit.addItems(["python3", "python"])
        self.individual_count_edit = QLineEdit('10')
        self.mutation_edit = QLineEdit('0.05')
        self.death_rate_edit = QLineEdit('0.5')
        #self.start_genomes_edit.setFixedHeight(200)
        # QLineEdit("[{'a':1,'b':2,'c':2,'d':2,'e':3}]")
        self.inactive_genome_info_edit = QLineEdit('{}')
        self.constraints_edit = QLineEdit("[]")#'a<b','b<=c'
        self.evo_options_edit = QLineEdit('{}')

        #right_vertical_layout = QVBoxLayout()
        #horizontal_layout.addLayout(right_vertical_layout)

        file_horizontal_layout = QHBoxLayout()
        file_horizontal_layout.addWidget(self.slave_file_edit, stretch=10)

        file_btn = QPushButton("...")
        file_btn.clicked.connect(self.select_file)
        file_btn.setMaximumWidth(30)
        file_horizontal_layout.addWidget(file_btn, stretch=0)


        right_vertical_layout.addLayout(file_horizontal_layout)

        #right_vertical_layout.addWidget(self.slave_file_edit)
        right_vertical_layout.addWidget(self.thread_number_edit)
        right_vertical_layout.addWidget(self.individual_count_edit)
        right_vertical_layout.addWidget(self.mutation_edit)
        right_vertical_layout.addWidget(self.death_rate_edit)
        #right_vertical_layout.addWidget(self.python_cmd_edit)
        right_vertical_layout.addWidget(self.inactive_genome_info_edit)
        right_vertical_layout.addWidget(self.constraints_edit)
        right_vertical_layout.addWidget(self.evo_options_edit)

        more_info_label = self.sidebar.add_widget(QLabel("..."), stretch=1)


        label = self.sidebar.add_widget(QLabel(u"\u24D8 " + "Start genomes:"), stretch=1)
        label.setToolTip("Genomes of the initial individuals. Example: [{'a':1,'b':2,'c':2}, {'a':3,'b':2,'c':1}] for two individuals with genes a,b and c")
        txt = QTextEdit()
        txt.setText("""[
{'a':1,'b':2,'c':2}
]""")
        self.start_genomes_edit = self.sidebar.add_widget(txt, stretch=100)


        #right_vertical_layout.addWidget(self.start_genomes_edit, stretch=5)

        more_info_label.setVisible(True)
        #pc_label.setVisible(False)
        ii_label.setVisible(False)
        c_label.setVisible(False)
        eo_label.setVisible(False)
        #self.python_cmd_edit.setVisible(False)
        self.inactive_genome_info_edit.setVisible(False)
        self.constraints_edit.setVisible(False)
        self.evo_options_edit.setVisible(False)

        def more_clicked(event):
            more_info_label.setVisible(False)
            #pc_label.setVisible(True)
            ii_label.setVisible(True)
            c_label.setVisible(True)
            #eo_label.setVisible(True)
            #self.python_cmd_edit.setVisible(True)
            self.inactive_genome_info_edit.setVisible(True)
            self.constraints_edit.setVisible(True)
            #self.evo_options_edit.setVisible(True)


        more_info_label.mouseReleaseEvent = more_clicked
        #more_info_label.clicked.connect(more_clicked)


    def On_Tab_Changed(self, i):
        if i is not None:
            tab = self.tabs.currentWidget()
            if hasattr(tab, 'ssm'):
                #self.update_status(tab, tab.name)
                ssm = self.tabs.currentWidget().ssm
                self.set_text(ssm, self.task_name_edit, 'name')
                self.set_text(ssm, self.slave_file_edit, 'slave_file')
                self.set_text(ssm, self.inactive_genome_info_edit, 'inactive_genome_info')
                self.set_text(ssm, self.thread_number_edit, 'thread_number')
                self.set_text(ssm, self.individual_count_edit, 'individual_count')
                self.set_text(ssm, self.mutation_edit, 'mutation')
                self.set_text(ssm, self.death_rate_edit, 'death_rate')
                self.set_text(ssm, self.start_genomes_edit, 'start_genomes')
                self.set_text(ssm, self.constraints_edit, 'constraints')
                #self.set_text(ssm, self.python_cmd_edit, 'python_cmd')
                self.set_text(ssm, self.evo_options_edit, 'evo_options')
                #self.refresh_view(tab)

    def get_help_txt(self):
        return '''Every tab corresponds to a folder in: Data/Evolution_Project_Clones/
This folders also contains the file execute.py which is used to start the evolution.
All genomes generate a file with the results and the genes when set_score is called in the slave file.
      
      
        
Local:
    The project folder (in which the "Data" folder is located) is copied into Data/Evolution_Project_Clones/task_name/



Remote Servers:
    For remote SSH servers the local folder (Data/Evolution_Project_Clones/task_name/) only contains some config files, 
    while the copy of the project folder is located in the user folder of the server.
    When the refresh button is clicked, the genome files are transferred back to the local folder.
    
    
    Requirements for remote server (tested on Ubuntu on AWS):
        -Python            (3)
        -screen
            
        -pip               (sudo apt install python3-pip)
        -PymoNNto          (pip install PymoNNto)
            
        -zip               (for transfer to remote server | sudo apt install zip)
        -unzip             (for transfer back to controller | sudo apt install unzip)
        -libgl1-mesa-glx   (if you have PyQT5 elements imported | sudo apt install libgl1-mesa-glx)
            
    Make sure that the python3 (python3 file.py) command is working on your system. "python file.py" (usually on windows) 
    is not supported. (create copy of python.exe named python3.exe if this problem occurs)
            
    When the evolution is started on a ssh server it creates a "screen" session which is named after the evolution name.

    Useful functions are:
        "screen -list" to show the screen sessions and their ids,
        "screen -r id" to connect to a session where "id" has to be replaced and
        "exit" to close a screen session you are connected to.
'''

    def create_execution_file(self, name, folder, file):
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
                devices={'multi_thread': #thread_number#},
                additional_evo_params=#evo_options#
                )

    if not evo.start(ui=False):
        evo.continue_evolution(ui=False)
        """

        print('generate execute.py...')
        exec_file = exec_file.replace('#name#', name)
        exec_file = exec_file.replace('#slave_file#', self.slave_file_edit.text())
        exec_file = exec_file.replace('#inactive_genome_info#', self.inactive_genome_info_edit.text())
        exec_file = exec_file.replace('#thread_number#', self.thread_number_edit.text())
        exec_file = exec_file.replace('#individual_count#', self.individual_count_edit.text())
        exec_file = exec_file.replace('#mutation#', self.mutation_edit.text())
        exec_file = exec_file.replace('#death_rate#', self.death_rate_edit.text())
        exec_file = exec_file.replace('#start_genomes#', self.start_genomes_edit.toPlainText().replace('\r', '').replace('\n', ''))
        exec_file = exec_file.replace('#constraints#', self.constraints_edit.text())
        exec_file = exec_file.replace('#evo_options#', self.evo_options_edit.text())

        md_file = open(file, "w")
        md_file.write(exec_file)
        md_file.close()
        return True

    def save_configuration(self, ssm):#SimpleStorageManager

        ssm.save_param('slave_file', self.slave_file_edit.text())
        ssm.save_param('inactive_genome_info', self.inactive_genome_info_edit.text())
        ssm.save_param('thread_number', self.thread_number_edit.text())
        ssm.save_param('individual_count', self.individual_count_edit.text())
        ssm.save_param('mutation', self.mutation_edit.text())
        ssm.save_param('death_rate', self.death_rate_edit.text())
        ssm.save_param('start_genomes', self.start_genomes_edit.toPlainText().replace('\r', '').replace('\n', ''))
        ssm.save_param('constraints', self.constraints_edit.text())
        #ssm.save_param('python_cmd', self.python_cmd_edit.text())
        ssm.save_param('evo_options', self.evo_options_edit.text())

        gene_keys = list(eval(self.start_genomes_edit.toPlainText().replace('\r', '').replace('\n', ''))[0].keys())
        ssm.save_param('gene_keys', gene_keys)

    def valid_configuration(self):
        valid_genomes = False
        try:
            sg = eval(self.start_genomes_edit.toPlainText().replace('\r', '').replace('\n', ''))
            for key in ['generation', 'score', 'id']:
                for genome in sg:
                    if key in genome:
                        genome.pop(key)
                        print(key, 'removed from genomes')
            self.start_genomes_edit.setText(str(sg))
            valid_genomes = True
        except:
            print('error parsing start genomes')

        if not valid_genomes:
            print('error parsing start genomes')

        return valid_genomes

    def add_additional_tab_elements(self, tab, name):

        def send(genome):
            user, host, password = split_ssh_user_host_password_string(tab.server,False)
            if host is None:
                host = 'localhost'
            print(socket_send(host, 'insert\r\n' + genome))

        def insert_click(event):
            self.text_input_dialog('enter genome', 'send', send, default_text='{}')


        insert_btn = self.tab.add_widget(QPushButton("insert genome"))
        insert_btn.clicked.connect(insert_click)

        self.tab.add_row(stretch=10)
        #self.Next_H_Block(stretch=10)
        add_evolution_plot_items(self, tab)
        tab.folder = get_epc_folder(self.folder) + '/' + name + '/'

    def refresh_view(self, tab):
        if tab.gene_keys is not None:
            update_evolution_plot(self, tab, tab.name, tab.gene_keys,data_folder=get_data_folder() + '/' + self.folder + '/' + tab.name + '/Data')

########################################################### Exception handling


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

sys.excepthook = except_hook

if __name__ == '__main__':
    UI_Evolution_Manager().show()

