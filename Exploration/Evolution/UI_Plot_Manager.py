from PymoNNto.Exploration.Evolution.common_UI import *
from PymoNNto.Exploration.Evolution.PlotQTObjects import *

class UI_Plot_Manager(Execution_Manager_UI_Base):

    def get_folder(self):
        return 'Plot_Project_Clones'

    def get_title(self):
        return 'Plot Monitor'

    def add_ui_elements(self):
        horizontal_layout = QHBoxLayout()
        self.sidebar_current_vertical_layout.addLayout(horizontal_layout)

        vertical_layout = QVBoxLayout()
        horizontal_layout.addLayout(vertical_layout)

        vertical_layout.addWidget(QLabel('slave file'))
        #vertical_layout.addWidget(QLabel('thread number'))
        vertical_layout.addWidget(QLabel('python cmd'))
        vertical_layout.addWidget(QLabel('runs'))

        self.slave_file_edit = QLineEdit('Exploration/Evolution/test_slave.py')
        #self.thread_number_edit = QLineEdit('4')
        self.python_cmd_edit = QLineEdit("python3")
        self.run_count_edit = QLineEdit('10')

        vertical_layout = QVBoxLayout()
        horizontal_layout.addLayout(vertical_layout)
        vertical_layout.addWidget(self.slave_file_edit)
        #vertical_layout.addWidget(self.thread_number_edit)
        vertical_layout.addWidget(self.python_cmd_edit)
        vertical_layout.addWidget(self.run_count_edit)


    def On_Tab_Changed(self, i):
        if i is not None:
            tab = self.tabs.currentWidget()
            if hasattr(tab, 'ssm'):
                self.update_status(tab, tab.name)
                ssm = self.tabs.currentWidget().ssm
                self.set_text(ssm, self.task_name_edit, 'name')
                self.set_text(ssm, self.slave_file_edit, 'slave_file')
                #self.set_text(ssm, self.thread_number_edit, 'thread_number')
                self.set_text(ssm, self.run_count_edit, 'run_count')
                self.set_text(ssm, self.python_cmd_edit, 'python_cmd')

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
        exec_file = """
import sys

py_file = open('#slave_file#', "r")
execution_string = py_file.read()
py_file.close()
        
def get_gene_id(gene):
    id = ''
    for key, value in gene.items():
        id += '#'+key+'@'+str(value)
    return id+'#'

def execute_local_file(genome):
    for arg in sys.argv:
        if 'genome=' in arg:
            sys.argv.remove(arg)
    sys.argv.append('genome=' + get_gene_id(genome))
    exec(execution_string)
    
for run in range(#run_count#):
    execute_local_file({'evo_name': '#name#', 'gen': run, 'id': run})   
        """

        print('generate execute.py...')
        exec_file = exec_file.replace('#name#', name)
        exec_file = exec_file.replace('#slave_file#', self.slave_file_edit.text())
        #exec_file = exec_file.replace('#thread_number#', self.thread_number_edit.text())
        exec_file = exec_file.replace('#run_count#', self.run_count_edit.text())

        md_file = open(file, "w")
        md_file.write(exec_file)
        md_file.close()
        return True

    def save_configuration(self, ssm):#SimpleStorageManager
        ssm.save_param('slave_file', self.slave_file_edit.text())
        #ssm.save_param('thread_number', self.thread_number_edit.text())
        ssm.save_param('run_count', self.run_count_edit.text())
        ssm.save_param('python_cmd', self.python_cmd_edit.text())


    def valid_configuration(self):
        return True

    def add_additional_tab_elements(self, tab, name):
        self.Next_H_Block(stretch=10)

        #tab.plot = self.Add_plot(title='results')

        tab.interactive_scatter = self.Add_element(InteractiveScatter())

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
    UI_Plot_Manager().show()
