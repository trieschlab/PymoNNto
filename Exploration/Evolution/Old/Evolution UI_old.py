from Exploration.UI_Base import *
import subprocess
from functools import partial




#process = subprocess.Popen(commands, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
#out, err = process.communicate()
#print(out)



#def subprocess_cmd(command):
#    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
#    proc_stdout = process.communicate()[0].strip()
#    return proc_stdout

#print(subprocess_cmd('echo a\r\necho b'))

#commands = 'cd C:/Users/Nutzer/Programmieren/tren2/Exploration/Evolution/ && python Evo_Plots.py'
#e = ["cd", "C:/"]
#output = subprocess.run(commands, stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
#print(output)

sys._excepthook = sys.excepthook

def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

sys.excepthook = exception_hook

class Evo_Task():

    def __init__(self, evo_name, main_command, just_refresh=False):
        self.evo_name = evo_name  # new_evolution
        self.main_command = main_command  # python3 OscillationTest_new3.py #srun ...
        self.just_refresh = just_refresh

class Evo_Server():

    def __init__(self, name, ssh_target, command_wrapper, evolution_path, use_screen, tasks=[]):
        self.name = name
        self.ssh_target = ssh_target  #local / vieth@poppy.fias.uni-frankfurt.de
        self.command_wrapper = command_wrapper#srun ...
        self.evolution_path = evolution_path #C:/.../Programmieren/Evolution/ or /Documents/
        self.use_screen = use_screen
        self.tasks=tasks


    def get_task_path(self, task):
        return self.evolution_path + task.evo_name

    def exec_cmd(self, cmd):
        print(cmd)
        return subprocess.run(cmd, stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')  # shell???

    def terminate(self, task):
        if self.ssh_target == 'local':
            print('not supported for local...')
        else:
            identifier = 'evolution_screen'

            #######search for instances
            output = subprocess.run(["ssh", self.ssh_target, "-t", "screen -ls"], stdout=subprocess.PIPE).stdout.decode('utf-8')

            instances = []

            for line in output.split('\n'):
                if identifier in line:
                    data = line.replace(' ', '').replace('\t', '').split('(')[0]
                    instances.append(data)

            if len(instances) == 0:
                print('nothing found')

            #######terminate found instances

            for i in instances:
                commands = "screen -X -S " + i + " quit"
                output = subprocess.run(["ssh", self.ssh_target, "-t", commands],
                                        stdout=subprocess.PIPE).stdout.decode('utf-8')
                print(i, 'terminated')

    def pull_update(self, task):
        #push
        output = self.exec_cmd('cd ../../ && git add . && git commit -m "'+task.evo_name+'" && git push')
        print(output)

        if self.ssh_target == 'local':
            output = self.exec_cmd('cd '+self.evolution_path+' && mkdir '+task.evo_name+' && cd '+task.evo_name+' && git clone git@gitlab.com:MariusVieth/tren2.git --depth=1')#+' && cd '+task.evo_name
        else:
            commands = "cd "+self.evolution_path+"; cd "+task.evo_name+"/tren2/; git stash; git pull"
            output = self.exec_cmd(["ssh", self.ssh_target, "-t", commands])#"vieth@poppy.fias.uni-frankfurt.de"
        print(output)


    def start_evo(self, task):

        cmd = task.main_command#'python3 OscillationTest_new3.py'

        if self.command_wrapper != '':
            cmd=self.command_wrapper+cmd
        # main_command = 'srun --partition=sleuths --reservation triesch-shared --mem=32000 --cpus-per-task=32 python3 OscillationTest_new3.py'


        commands = 'cd '+self.evolution_path + task.evo_name+'/tren2/Exploration/Evolution/; screen -dmS '+task.evo_name+' sh; screen -S '+task.evo_name+' -X stuff "' + cmd+ ' '+ task.evo_name + '\r\n"'
        output = subprocess.run(["ssh", self.ssh_target, "-t", commands], stdout=subprocess.PIPE).stdout.decode('utf-8')
        print(output)


    def git_transfer(self,task):
        #push
        output = self.exec_cmd('cd ../../ && git add . && git commit -m "'+task.evo_name+'" && git push')
        print(output)

        #pull
        if self.ssh_target == 'local':
            output = self.exec_cmd('cd '+self.evolution_path+' && mkdir '+task.evo_name+' && cd '+task.evo_name+' && git clone git@gitlab.com:MariusVieth/tren2.git --depth=1')#+' && cd '+task.evo_name
        else:
            commands = "cd "+self.evolution_path+"; mkdir "+task.evo_name+"; cd "+task.evo_name+"; git clone git@gitlab.com:MariusVieth/tren2.git --depth=1" #git stash; git pull
            output = self.exec_cmd(["ssh", self.ssh_target, "-t", commands])#"vieth@poppy.fias.uni-frankfurt.de"
        print(output)

    def refresh_text(self, task):
        cmd = ["ssh", self.ssh_target, "-t", "screen -r 1578"]
        output = self.exec_cmd(cmd)
        return output

    def get_progress(self, task):

        if self.ssh_target == 'local':
            cmd = "cd " + self.get_task_path(task) + "/tren2/Exploration/Evolution/ && python Evo_Plots.py"
        else:
            cmd = ["ssh", self.ssh_target, "-t", "cd " + self.evolution_path + task.evo_name + "/tren2/Exploration/Evolution/; python3 Evo_Plots.py"]

        output=self.exec_cmd(cmd)

        #print(output)

        y = []

        for line in output.replace('\r','').split('\n'):
            data = line.split(' ')
            if len(data) == 2 and data[0].isdigit() and data[1].replace('.', '').replace('-', '').isdigit():
                y.append(float(data[1]))

        if 'Pfad nicht finden' in output or len(y) == 0:
            print('Keine Daten gefunden...')

        return y

        #plt.plot(y)
        #plt.show()




class EVO_UI(UI_Base):

    def __init__(self):
        super().__init__(None, label='EVO manager')

        self.reduced_layout = False

        self.evo_servers = []

        # load_evo_controllers...
        task1 = Evo_Task(main_command='python3 Multithreaded_Evolution.py', evo_name='.', just_refresh=True)
        self.evo_servers.append(Evo_Server(name='XPS Main',
                                               ssh_target='local',
                                               command_wrapper='',
                                               evolution_path='C:/Users/Nutzer/Programmieren/',
                                               use_screen=False,
                                               tasks=[task1]))



        task2 = Evo_Task(main_command='python3 Multithreaded_Evolution.py', evo_name='evo_test2')
        self.evo_servers.append(Evo_Server(name='XPS Evo',
                                               ssh_target='local',
                                               command_wrapper='',
                                               evolution_path='C:/Users/Nutzer/Programmieren/Evolution/',
                                               use_screen=False,
                                               tasks=[task2]))


        task3=Evo_Task(main_command='python3 Multithreaded_Evolution.py', evo_name='som_pv_improvement_15_04')
        self.evo_servers.append(Evo_Server(name='Poppy',
                                               ssh_target='vieth@poppy.fias.uni-frankfurt.de',
                                               command_wrapper='',
                                               evolution_path='Documents/Evolution/',
                                               use_screen=True,
                                               tasks=[task3]))


        task4=Evo_Task(main_command='python3 Multithreaded_Evolution.py', evo_name='evo_all_no_stdp')
        self.evo_servers.append(Evo_Server(name='Slurm',
                                               ssh_target='vieth@poppy.fias.uni-frankfurt.de',
                                               command_wrapper='srun --partition=sleuths --reservation triesch-shared --mem=32000 --cpus-per-task=6 ',
                                               evolution_path='Documents/SRUN_Evolution/',
                                               use_screen=True,
                                               tasks=[task4]))

        task5=Evo_Task(main_command='python3 Multithreaded_Evolution.py', evo_name='evo_short_no_stdp')
        self.evo_servers.append(Evo_Server(name='SlurmXMEN',
                                               ssh_target='vieth@poppy.fias.uni-frankfurt.de',
                                               command_wrapper='srun --partition=x-men --mem=32000 --cpus-per-task=32 ',
                                               evolution_path='Documents/XMEN_Evolution/',
                                               use_screen=True,
                                               tasks=[task5]))

        task6=Evo_Task(main_command='python3 Multithreaded_Evolution.py', evo_name='new_grammar_new_params_16_03_5')
        self.evo_servers.append(Evo_Server(name='Desktop',
                                               ssh_target='marius@hey3kmuagjunsk2b.myfritz.net',
                                               command_wrapper='',
                                               evolution_path='Evolution/',
                                               use_screen=True,
                                               tasks=[task6]))


        for evo_server in self.evo_servers:
            self.main_tab = self.Next_Tab(evo_server.name, stretch=0.0)

            #self.Next_H_Block(stretch=0.1)
            #info = QLabel(self.main_window)
            #info.setText('main_command: '+evo_server.command_wrapper)
            #self.Add_element(info)

            #self.Next_H_Block(stretch=0.1)
            #info = QLabel(self.main_window)
            #info.setText('evolution_path: '+evo_server.evolution_path)
            #self.Add_element(info)

            #self.Next_H_Block(stretch=0.1)
            #info = QLabel(self.main_window)
            #info.setText('use screen: ' + str(evo_server.use_screen))
            #self.Add_element(info)


            for task in evo_server.tasks:
                self.Next_H_Block(stretch=0.1)
                info = QLabel(self.main_window)
                info.setText(str(task.evo_name) + ' (' + str(task.main_command)+')')
                self.Add_element(info)

                #self.Next_H_Block(stretch=0.1)
                #info = QLabel(self.main_window)
                #info.setText('main_command: ' + str(task.main_command))
                #self.Add_element(info)

                self.Next_H_Block(stretch=10)

                curve1,curve2=self.Add_plot_curve('plot', number_of_curves=2)

                #text_box = QTextEdit(self.main_window)
                #self.Add_element(text_box)


                self.button_stack = QVBoxLayout(self.main_window)
                self.current_H_block.addLayout(self.button_stack)

                #self.Next_H_Block(stretch=1)
                #def refresh_text(e, t):
                #    text_box.setText(e.refresh_text(t))
                #refresh_text_btn = QPushButton('refresh_text', self.main_window)
                #refresh_text_btn.clicked.connect(partial(refresh_text, evo_server, task))
                #self.button_stack.addWidget(refresh_text_btn)

                def refresh(e, t, c1, c2):
                    data=e.get_progress(t)
                    c1.setData(data)

                    #smoothing
                    data2=data.copy()
                    if len(data)>1:
                        for _ in range(20):
                            for i in range(len(data)):
                                if i==0:
                                    data2[i] = (data2[i] + data2[i + 1]+data[i]) / 3.0
                                elif i==len(data)-1:
                                    data2[i] = (data2[i] + data2[i - 1]+data[i]) / 3.0
                                else:
                                    data2[i] = (data2[i] + data2[i - 1] + data2[i + 1]) / 3.0

                    c2.setData(data2)


                refresh_btn = QPushButton('refresh', self.main_window)
                refresh_btn.clicked.connect(partial(refresh, evo_server, task, curve1,curve2))
                self.button_stack.addWidget(refresh_btn)
                #self.Add_element(refresh_btn)

                if not task.just_refresh:
                    def terminate(e, t):
                        e.terminate(t)

                    terminate_btn = QPushButton('terminate', self.main_window)
                    terminate_btn.clicked.connect(partial(terminate, evo_server, task))
                    self.button_stack.addWidget(terminate_btn)
                    #self.Add_element(terminate_btn)

                    def transfer(e, t):
                        e.git_transfer(t)

                    transfer_btn = QPushButton('transfer', self.main_window)
                    transfer_btn.clicked.connect(partial(transfer, evo_server, task))
                    self.button_stack.addWidget(transfer_btn)
                    #self.Add_element(transfer_btn)

                    def start_evo(e, t):
                        e.start_evo(t)

                    start_evo_btn = QPushButton('execute', self.main_window)
                    start_evo_btn.clicked.connect(partial(start_evo, evo_server, task))
                    self.button_stack.addWidget(start_evo_btn)
                    #self.Add_element(start_evo_btn)

                    def pull_update(e, t):
                        e.pull_update(t)

                    pull_update_btn = QPushButton('pull update', self.main_window)
                    pull_update_btn.clicked.connect(partial(pull_update, evo_server, task))
                    self.button_stack.addWidget(pull_update_btn)


            self.Next_H_Block()
            info = QLabel(self.main_window)
            info.setText('SSH: ' + evo_server.ssh_target + ' | SCREEN: ' + str(evo_server.use_screen) + ' | PATH: ' + evo_server.evolution_path + ' | SLURM: ' + evo_server.command_wrapper)
            self.Add_element(info)

        # self.Add_element(self.ff_btn, sidebar=True)






EVO_UI().show()
