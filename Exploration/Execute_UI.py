from PymoNNto.Exploration.Evolution.common_UI import *
from PymoNNto.Exploration.Evolution.PlotQTObjects import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.Helper.syntax import *

class Execute_UI(Execution_Manager_UI_Base):

    def get_folder(self):
        return 'Plot_Project_Clones'

    def get_title(self):
        return 'Execution Manager'

    def add_ui_elements(self, left_vertical_layout, right_vertical_layout):

        #horizontal_layout = QHBoxLayout()
        #self.sidebar_current_vertical_layout.addLayout(horizontal_layout)

        #vertical_layout = QVBoxLayout()
        #left_vertical_layout.addLayout(vertical_layout)
        left_vertical_layout.addWidget(QLabel('slave file'))
        #left_vertical_layout.addWidget(QLabel('thread number'))
        #left_vertical_layout.addWidget(QLabel('python cmd'))
        #left_vertical_layout.addWidget(QLabel('runs'))


        #self.slave_file_edit = QLineEdit('Exploration/Evolution/example_slave.py')
        self.slave_file_edit = QLineEdit('')
        self.slave_file_edit.textChanged.connect(self.check_file)
        self.slave_file_edit.setText('Exploration/Evolution/example_slave.py')

        #self.thread_number_edit = QLineEdit('4')
        #self.python_cmd_edit = QLineEdit("python")
        #self.run_count_edit = QLineEdit('10')

        #vertical_layout = QVBoxLayout()
        #horizontal_layout.addLayout(vertical_layout)


        #right_vertical_layout.addWidget(self.slave_file_edit)

        file_horizontal_layout = QHBoxLayout()
        file_horizontal_layout.addWidget(self.slave_file_edit, stretch=10)

        file_btn = QPushButton("...")
        file_btn.clicked.connect(self.select_file)
        file_btn.setMaximumWidth(30)
        file_horizontal_layout.addWidget(file_btn, stretch=0)


        right_vertical_layout.addLayout(file_horizontal_layout)


        #right_vertical_layout.addWidget(self.thread_number_edit)
        #right_vertical_layout.addWidget(self.python_cmd_edit)
        #right_vertical_layout.addWidget(self.run_count_edit)

        ec_label=QLabel(u"\u24D8 " + 'Execution code:')
        ec_label.setToolTip("file_exec({'gene1': 1, ...})")

        self.sidebar.add_widget(ec_label, stretch=0)
        #self.Add_element(ec_label, sidebar=True, stretch=0)

        self.qte = QPlainTextEdit()

        self.qte.highlight = PythonHighlighter(self.qte.document(), ['neurons', 'synapses', 'network', 'file_exec'])
        font = QFont()
        font.setPointSize(9)
        self.qte.setFont(font)

        self.qte.setPlainText("""for _ in range(100):
    file_exec({})
""")
        self.qte.setStyleSheet("QPlainTextEdit { background-color: rgb(43, 43, 43); }")
        self.sidebar.add_widget(self.qte, stretch=100)
        #self.Add_element(self.qte, sidebar=True, stretch=100)


    def On_Tab_Changed(self, i):
        if i is not None:
            tab = self.tabs.currentWidget()
            if hasattr(tab, 'ssm'):
                self.update_status(tab, tab.name)
                ssm = self.tabs.currentWidget().ssm
                self.set_text(ssm, self.task_name_edit, 'name')
                self.set_text(ssm, self.slave_file_edit, 'slave_file')
                #self.set_text(ssm, self.thread_number_edit, 'thread_number')
                #self.set_text(ssm, self.run_count_edit, 'run_count')
                #self.set_text(ssm, self.python_cmd_edit, 'python_cmd')

    def get_help_txt(self):
        return '''Every tab corresponds to a folder in:
Data/Plot_Project_Clones/

For remote SSH servers the local folder only contains some config files while the project copy is located in the user folder of the server.

When the evolution is started on a ssh server it creates a "screen" session which is named after the evolution name.

Useful functions are:

    "screen -list" to show the screen sessions and their ids,
    "screen -r id" to connect to a session where "id" has to be replaced and
    "exit" to close a screen session you are connected to.

The project folders also contain the file execute.py which is used to start the evolution.

All genomes generate a file with the results and the genes when set_score is called in the slave file. Which are transferred to the local folder when the state is refreshed.
'''

    def create_execution_file(self, name, folder, file):

        #from PymoNNto.Exploration.Evolution.Interface_Functions import *

        exec_file = """from PymoNNto import *
from PymoNNto.Exploration.Evolution.Interface_Functions import *
from PymoNNto.Exploration.HelperFunctions.IteratorFunctions import *

ids = StorageManagerGroup('evo_name').get_param_list('id', remove_None=True)
if len(ids) == 0:
    execution_counter_ = 0
else:
    execution_counter_ = np.max(ids) + 1

def file_exec(genes):
    global execution_counter_
    execute_local_file(file='#file#', evo_name='#name#', evo_id=execution_counter_, genome=genes)
    execution_counter_+=1
    
"""+self.qte.toPlainText()
#        """
#from PymoNNto.Exploration.Evolution.Interface_Functions import *
#import sys
#
#for run in range(#run_count#):
#    execute_local_file('#slave_file#', {'evo_name': '#name#', 'generation': run, 'id': run})
#        """

        print('generate execute.py...')
        exec_file = exec_file.replace('#name#', name)
        exec_file = exec_file.replace('#file#', self.slave_file_edit.text())
        #exec_file = exec_file.replace('#thread_number#', self.thread_number_edit.text())
        #exec_file = exec_file.replace('#runs#', self.run_count_edit.text())

        md_file = open(file, "w")
        md_file.write(exec_file)
        md_file.close()
        return True

    def save_configuration(self, ssm):#SimpleStorageManager
        ssm.save_param('slave_file', self.slave_file_edit.text())
        #ssm.save_param('thread_number', self.thread_number_edit.text())
        #ssm.save_param('run_count', self.run_count_edit.text())
        #ssm.save_param('python_cmd', self.python_cmd_edit.text())


    def valid_configuration(self):
        return True

    def add_additional_tab_elements(self, tab, name):
        self.tab.add_row(stretch=10)
        #self.Next_H_Block(stretch=10)

        #tab.plot = self.Add_plot(title='results')

        tab.interactive_scatter = self.tab.add_widget(InteractiveScatter(default_x='id', default_y='score', coloration_param='score'))

        #add_evolution_plot_items(self, tab)
        #tab.folder = get_epc_folder(self.folder) + '/' + name + '/'

    def refresh_view(self, tab):
        #tab.plot scatter...

        smg = StorageManagerGroup(tab.name, data_folder=get_data_folder() + '/' + self.folder + '/' + tab.name + '/Data')
        tab.interactive_scatter.add_StorageManagerGroup(smg)
        tab.interactive_scatter.refresh_data()

        print(smg.get_param_list('score'))

########################################################### Exception handling


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

sys.excepthook = except_hook

if __name__ == '__main__':
    Execute_UI().show()
