import subprocess
import shutil
import datetime
import time
import os

#def zipdir(path, ziph):
#    # ziph is zipfile handle
#    for root, dirs, files in os.walk(path):
#        for file in files:
#            ziph.write(os.path.join(root, file))

class Evolution_Server_Base:

    def __init__(self, name, main_path):
        self.name = name
        self.main_path = main_path
        self.temp_zip_dir = '../../../temp_zip_evolution/'

    def exec_cmd(self, cmd, shell=False, cwd=None):
        if type(cmd) is tuple:
            if len(cmd)>2:
                cwd=cmd[2]
            shell = cmd[1]
            cmd = cmd[0]
        print(cmd)

        #output = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
        if cmd is not None:
            output = subprocess.run(cmd, stdout=subprocess.PIPE, shell=shell, cwd=cwd).stdout.decode('utf-8')
            print(output)
            return output
        else:
            return ''

    def transfer(self, evo_name):
        #compress
        shutil.make_archive(self.temp_zip_dir+evo_name, 'zip', '../../../Self-Organizing-Recurrent-Network-Simulator_Dev')
        #transfer
        self.exec_cmd(self.get_transfer_cmd(evo_name))
        #extract
        self.exec_cmd(self.get_extract_cmd(evo_name))
        os.remove(self.temp_zip_dir+evo_name+'.zip')

    def execute(self, evo_name, arguments):
        self.exec_cmd(self.get_Evo_Execute_cmd(evo_name, arguments))

    def terminate_screen(self, evo_name):
        self.exec_cmd(self.get_terminate_screen_cmd(evo_name))

    def remove_evo(self, evo_name):
        self.exec_cmd(self.get_remove_cmd(evo_name))

    def parse_plot_data_output(self, output):
        y = []

        for line in output.replace('\r', '').split('\n'):
            data = line.split(' ')
            if len(data) == 2 and data[0].isdigit() and data[1].replace('.', '').replace('-', '').isdigit():
                y.append(float(data[1]))

        if 'Pfad nicht finden' in output or len(y) == 0:
            print('Keine Daten gefunden...')

        return y

    def plot_data(self, evo_name):
        output = self.exec_cmd(self.get_plot_cmd(evo_name))
        return self.parse_plot_data_output(output)


    def running_evos(self):
        result = []
        output = self.exec_cmd(self.get_running_list_cmd())

        for l in output.splitlines():
            if '	' in l:
                dot_split = l.split('.')
                if len(dot_split) > 1:
                    space_split = dot_split[1].split('	')
                    if len(space_split) > 0:
                        result.append(space_split[0])
                        #print('found' + space_split[0])

        return result

    def evolution_list(self):
        result = {}

        output = self.exec_cmd(self.get_evo_list_cmd())

        for l in output.splitlines():

            while '  ' in l:
                l = l.replace('  ', ' ')

            space_split = l.split(' ')
            if len(space_split) == 9 and l[-1] != '.':

                date_time_obj = datetime.datetime.strptime(space_split[5].replace('Mai','May')+' '+space_split[6]+' '+space_split[7], '%b %d %H:%M')
                result[date_time_obj] = space_split[-1]


        result_list = []
        for key in reversed(sorted(list(result.keys()))):
            result_list.append(result[key])

        return result_list

    def open_terminal(self, evo_name):
        os.system("start cmd.exe @cmd /k " + " ".join(self.get_open_terminal_cmd(evo_name)))

    def get_open_terminal_cmd(self, evo_name):
        return 'screen -r '+evo_name

    def get_plot_cmd(self, evo_name):
        return None

    def get_Evo_Execute_cmd(self, evo_name, arguments):
        return None

    def get_transfer_cmd(self, evo_name):
        return None

    def get_extract_cmd(self, evo_name):
        return None

    def get_python_exec(self, arguments, path='', python='python3'):
        screen_cmd = python + " "+path+"Multithreaded_Evolution.py"
        for arg in arguments:
            screen_cmd += " "+arg.replace(' ', '')
        return screen_cmd

    def get_terminate_screen_cmd(self, evo_name):
        return 'screen -XS '+evo_name+' quit'

    def get_remove_cmd(self, evo_name):
        return 'cd '+self.main_path+'; rm -r '+evo_name

    def get_evo_list_cmd(self):
        return 'cd '+self.main_path+'; ls -la'

    def get_running_list_cmd(self):
        return 'screen -ls'

    def get_plot_cmd(self, evo_name):
        return 'cd ' + self.main_path + evo_name + "/Exploration/Evolution/; python3 Evo_Plots.py"

    def get_Evo_Execute_cmd(self, evo_name, arguments):
        pexc=self.get_python_exec(arguments)
        commands = 'cd ' + self.main_path + evo_name + '/Exploration/Evolution/; screen -dmS ' + evo_name + ' sh; screen -S ' + evo_name + ' -X stuff "' + pexc + ' \r\n"'
        return commands

class Evolution_Server_Local_Windows(Evolution_Server_Base):

    def get_terminate_screen_cmd(self, evo_name):
        print('not supported for windows')
        return None

    def get_running_list_cmd(self):
        print('not supported for windows')
        return None#'C:\\cygwin64\\bin\\screen.exe -ls'

    def get_remove_cmd(self, evo_name):
        print(self.main_path + evo_name)
        shutil.rmtree(self.main_path + evo_name)
        return None

    def evolution_list(self):
        result = {}

        output = self.exec_cmd(self.get_evo_list_cmd())

        for l in output.splitlines():

            while '  ' in l:
                l = l.replace('  ', ' ')

            space_split = l.split(' ')
            if len(space_split) == 4 and l[-1] != '.' and space_split[0]!='':
                date_time_obj = datetime.datetime.strptime(space_split[0]+' '+space_split[1], '%d.%m.%Y %H:%M')
                result[date_time_obj] = space_split[-1]


        result_list = []
        for key in reversed(sorted(list(result.keys()))):
            result_list.append(result[key])

        print(result)

        return result_list

    def __init__(self, name, main_path):
        super().__init__(name, main_path)
        self.temp_zip_dir = main_path

    def get_evo_list_cmd(self):
        return 'dir '+self.main_path.replace('/', '\\'), True #-la does not exist

    def get_extract_cmd(self, evo_name):
        shutil.unpack_archive(self.main_path + evo_name + '.zip', self.main_path + evo_name , 'zip')
        #commands = 'dir'#,'Expand-Archive ' + self.main_path.replace('/','\\') + evo_name + '.zip' #unzip=>Expand-Archive + no zip delete (same device)
        return None

    #def get_Evo_Execute_cmd(self, evo_name, arguments):
        #return commands.replace('/', '\\'), True, path.replace('/', '\\')

    def get_plot_cmd(self, evo_name):
        return 'python' + self.main_path + evo_name + '/Exploration/Evolution/Evo_Plots.py'

    def execute(self, evo_name, arguments):
        path = self.main_path + evo_name + '/Exploration/Evolution/'
        path=path.replace('/', '\\')
        pexc = self.get_python_exec(arguments, python='python')
        os.system("start cmd.exe "+path+" @cmd /k "+pexc)

        #self.exec_cmd('screen -d -m '+pexc, True, path)

        #c1='C:\\cygwin64\\bin\\screen.exe -dmS ' + evo_name
        #self.exec_cmd(c1.replace('/', '\\'), True, path)
        #c2='C:\\cygwin64\\bin\\screen.exe -S ' + evo_name + ' -X stuff "' + pexc + ' \r\n"'
        #self.exec_cmd(c2.replace('/', '\\'), True, path)

class Evolution_Server_SSH(Evolution_Server_Base):

    def __init__(self, name, main_path, ssh_target):
        super().__init__(name, main_path)
        self.ssh_target = ssh_target

    def ssh_wrap_cmd(self, commands):
        return ["ssh", self.ssh_target, "-t", commands]

    def get_extract_cmd(self, evo_name):
        commands = 'mkdir ' + self.main_path + evo_name + '; cd '+self.main_path+'; unzip ' +evo_name+'.zip -d '+ evo_name + '; rm '+evo_name+'.zip'
        return self.ssh_wrap_cmd(commands)

    def get_terminate_screen_cmd(self, evo_name):
        return self.ssh_wrap_cmd(super().get_terminate_screen_cmd(evo_name))

    def get_remove_cmd(self, evo_name):
        return self.ssh_wrap_cmd(super().get_remove_cmd(evo_name))

    def get_open_terminal_cmd(self, evo_name):
        return self.ssh_wrap_cmd(super().get_open_terminal_cmd(evo_name))

    def get_evo_list_cmd(self):
        return self.ssh_wrap_cmd(super().get_evo_list_cmd())

    def get_running_list_cmd(self):
        return self.ssh_wrap_cmd(super().get_running_list_cmd())

    def get_plot_cmd(self, evo_name):
        return self.ssh_wrap_cmd(super().get_plot_cmd(evo_name))

    def get_transfer_cmd(self, evo_name):
        src = self.temp_zip_dir+evo_name+'.zip'
        dst = self.ssh_target + ':' + self.main_path
        return 'scp ' + src + ' ' + dst

    def get_Evo_Execute_cmd(self, evo_name, arguments):
        return self.ssh_wrap_cmd(super().get_Evo_Execute_cmd(evo_name, arguments))

class Evolution_Server_SSH_Slurm(Evolution_Server_SSH):

    def __init__(self, name, main_path, ssh_target, slurm_wrapper):
        super().__init__(name, main_path, ssh_target)
        self.slurm_wrapper = slurm_wrapper

    def get_terminate_screen_cmd(self, evo_name):
        return self.ssh_wrap_cmd('scancel --name ' + evo_name)

    def terminate_screen(self, evo_name):
        self.exec_cmd(self.get_terminate_screen_cmd(evo_name))
        time.sleep(2)

    def get_running_list_cmd(self):
        return self.ssh_wrap_cmd('squeue -u vieth')

    def get_Evo_Execute_cmd(self, evo_name, arguments):
        pexc=self.get_python_exec(arguments)
        commands = 'cd ' + self.main_path + evo_name + '/Exploration/Evolution/; ' + self.slurm_wrapper.replace('*command*', 'sbatch') + ' --job-name='+ evo_name + ' --wrap="' + pexc + '"'
        return self.ssh_wrap_cmd(commands)

    def running_evos(self):
        result = []
        output = self.exec_cmd(self.get_running_list_cmd())

        for l in output.splitlines():

            while '  ' in l:
                l = l.replace('  ', ' ')

            if not 'NAME' in l:
                dot_split = l.split(' ')
                if len(dot_split) > 3:
                    result.append(dot_split[3])

        print(result)

        return result

class XPS_Server(Evolution_Server_Local_Windows):
    def __init__(self):
        super().__init__('XPS', '../../../Evolution/')
        self.cores=6

class BV_Server(Evolution_Server_SSH):
    def __init__(self):
        super().__init__('BV', 'Evolution/', 'marius@hey3kmuagjunsk2b.myfritz.net')
        self.cores = 2

class Poppy_Server(Evolution_Server_SSH):
    def __init__(self):
        super().__init__('Poppy', 'Documents/Evolution/', 'vieth@poppy.fias.uni-frankfurt.de')
        self.cores = 4

class XMEN_Server(Evolution_Server_SSH_Slurm):
    def __init__(self):
        super().__init__('SlurmXMEN', 'Documents/XMEN_Evolution/', 'vieth@poppy.fias.uni-frankfurt.de', '*command* --partition=x-men --mem=32000 --cpus-per-task=32')
        self.cores = 2

class Sleuths_Server(Evolution_Server_SSH_Slurm):
    def __init__(self):
        super().__init__('SlurmSleuths', 'Documents/Sleuths_Evolution/', 'vieth@poppy.fias.uni-frankfurt.de', '*command* --partition=sleuths --reservation triesch-shared --mem=8000 --cpus-per-task=1')#srun #32000 !!!
        self.cores = 2

#class XPS_Server(Evolution_Server_Base):
#    def __init__(self):
#        super().__init__('XPS', '???/')

def get_devices(local=True):
    result = [BV_Server(), Poppy_Server(),XMEN_Server(), Sleuths_Server()]#
    if local:
        result += [XPS_Server()]#, Poppy_Server(), XMEN_Server(), Sleuths_Server(), XPS_Server()
    return result