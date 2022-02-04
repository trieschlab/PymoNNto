from PymoNNto.Exploration.Evolution.common_UI import *

class UI_Evolution_Manager(Execution_Manager_UI_Base):

    def get_folder(self):
        return 'Evolution_Project_Clones'

    def get_title(self):
        return 'Evolution Monitor'

    def add_ui_elements(self):
        horizontal_layout = QHBoxLayout()
        self.sidebar_current_vertical_layout.addLayout(horizontal_layout)

        vertical_layout = QVBoxLayout()
        horizontal_layout.addLayout(vertical_layout)
        vertical_layout.addWidget(QLabel('slave file'))
        vertical_layout.addWidget(QLabel('thread number'))
        vertical_layout.addWidget(QLabel('python cmd'))
        vertical_layout.addWidget(QLabel('individual count'))
        vertical_layout.addWidget(QLabel('mutation'))
        vertical_layout.addWidget(QLabel('death rate'))
        vertical_layout.addWidget(QLabel('start geneomes'))
        vertical_layout.addWidget(QLabel('inactive info'))
        vertical_layout.addWidget(QLabel('constriants'))
        vertical_layout.addWidget(QLabel('evo options'))

        self.slave_file_edit = QLineEdit('Exploration/Evolution/test_slave.py')
        self.thread_number_edit = QLineEdit('4')
        self.python_cmd_edit = QLineEdit("python3")
        self.individual_count_edit = QLineEdit('10')
        self.mutation_edit = QLineEdit('0.05')
        self.death_rate_edit = QLineEdit('0.5')
        self.start_genomes_edit = QLineEdit("[{'a':1,'b':2,'c':2,'d':2,'e':3}]")
        self.inactive_genome_info_edit = QLineEdit('{}')
        self.constraints_edit = QLineEdit("['a<b','b<=c']")
        self.evo_options_edit = QLineEdit('{}')

        vertical_layout = QVBoxLayout()
        horizontal_layout.addLayout(vertical_layout)
        vertical_layout.addWidget(self.slave_file_edit)
        vertical_layout.addWidget(self.thread_number_edit)
        vertical_layout.addWidget(self.python_cmd_edit)
        vertical_layout.addWidget(self.individual_count_edit)
        vertical_layout.addWidget(self.mutation_edit)
        vertical_layout.addWidget(self.death_rate_edit)
        vertical_layout.addWidget(self.start_genomes_edit)
        vertical_layout.addWidget(self.inactive_genome_info_edit)
        vertical_layout.addWidget(self.constraints_edit)
        vertical_layout.addWidget(self.evo_options_edit)

    def On_Tab_Changed(self, i):
        if i is not None:
            tab = self.tabs.currentWidget()
            if hasattr(tab, 'ssm'):
                self.update_status(tab, tab.name)
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
                self.set_text(ssm, self.python_cmd_edit, 'python_cmd')
                self.set_text(ssm, self.evo_options_edit, 'evo_options')

    def get_help_txt(self):
        return '''Every tab corresponds to a folder in:
        Data/Evolution_Project_Clones/

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
        exec_file = exec_file.replace('#start_genomes#', self.start_genomes_edit.text())
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
        ssm.save_param('start_genomes', self.start_genomes_edit.text())
        ssm.save_param('constraints', self.constraints_edit.text())
        ssm.save_param('python_cmd', self.python_cmd_edit.text())
        ssm.save_param('evo_options', self.evo_options_edit.text())

        gene_keys = list(eval(self.start_genomes_edit.text())[0].keys())
        ssm.save_param('gene_keys', gene_keys)

    def valid_configuration(self):
        valid_genomes = False
        try:
            sg = eval(self.start_genomes_edit.text())
            for key in ['gen', 'score', 'id']:
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
        self.Next_H_Block(stretch=10)
        add_evolution_plot_items(self, tab)
        tab.folder = get_epc_folder(self.folder) + '/' + name + '/'

    def refresh_view(self, tab):
        update_evolution_plot(self, tab, tab.name, tab.gene_keys,data_folder=get_data_folder() + '/' + self.folder + '/' + tab.name + '/Data')

if __name__ == '__main__':
    UI_Evolution_Manager().show()

