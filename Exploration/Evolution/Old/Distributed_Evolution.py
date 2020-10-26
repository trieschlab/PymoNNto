import sys
sys.path.append('../../')

from Exploration.Evolution.Evolution import *
from multiprocessing import Process, Queue, Value

import time

import subprocess
from functools import partial

def string_2_array(s):
    return [float(nr_str) for nr_str in s.split('_')]

def array_2_string(a,round=False):
    result=''
    for i, nr in enumerate(a):
        temp=float(nr)
        if round:
            temp=np.round(temp, 6)
        result += str(temp)
        if i is not len(a)-1:
            result += '_'
    return result

def parse_sys(tag='test', ind=[]):
    import sys
    print(sys.argv)
    if len(sys.argv) == 3:
        tag = sys.argv[1]
        ind = string_2_array(sys.argv[2])
    return tag, ind


def get_file_name(tag, ind):
    return '_'+tag+'_'+array_2_string(ind, True)+'.txt'


def save_score(score, tag, ind):
    if score is not None:
        filename = get_data_folder()+'/Evo/' + get_file_name(tag, ind)  # evo
        print('saved to '+filename)
        f = open(filename, "w")  # 'a':appand
        f.write('score:'+str(score))
        f.close()


class Execution_Instance:

    def __init__(self, device, individual, parent):
        self.device = device
        self.thread = self.choose_core()
        self.individual = individual
        self.parent = parent
        self.result = None
        self.rand_num = np.random.randint(0, 1000000)

    def choose_core(self):
        core=-1
        while core==-1 or found:
            core+=1
            found=False
            for instance in self.device.running_instances:
                if instance.thread==core:
                    found=True

        if core>self.device.cores:
            print('warning: more running instances ('+str(core)+') than cores ('+self.device.cores+') on machine '+self.device.name)

        return core

    def terminate(self):
        try:
            identifier = self.get_tag()+'_'+str(self.thread)

            #######search for instances
            output = self.parent.exec_cmd(["ssh", self.device.ssh_target, "-t", "screen -ls"])

            instances = []

            for line in output.split('\n'):
                if identifier in line:
                    data = line.replace(' ', '').replace('\t', '').split('(')[0]
                    instances.append(data)

            #if len(instances) == 0:
            #    print('nothing found')

            #######terminate found instances

            for i in instances:
                commands = "screen -X -S " + i + " quit"
                output = self.parent.exec_cmd(["ssh", self.device.ssh_target, "-t", commands])
                #print(i, 'terminated')
        except:
            print('termination fialed at '+self.device.name)

    def get_tag(self):
        return self.parent.name+'_'+str(self.rand_num)+'_'+self.device.name

    def execute(self):
        try:
            #self.parent.evaluation_path
            #.main_command
            #str(self.individual).replace(' ','').replace('[','').replace(']','')
            cmd = self.device.python_command + ' ' + self.parent.evaluation_file+' '+self.get_tag()+' '+array_2_string(self.individual)#'python3 OscillationTest_new3.py tag ind thread'

            if self.device.command_wrapper != '':
                cmd=self.device.command_wrapper+cmd
            # main_command = 'srun --partition=sleuths --reservation triesch-shared --mem=32000 --cpus-per-task=32 python3 OscillationTest_new3.py'
            commands=''
            commands += 'cd '+self.device.evolution_path + self.parent.name+'/tren2/'+self.parent.evaluation_path+';'
            commands += ' screen -dmS '+self.get_tag()+'_'+str(self.thread)+' sh;'
            commands += ' screen -S '+self.get_tag()+'_'+str(self.thread)+' -X stuff "' +cmd+ '\r\n"'
            #print(commands)
            output = self.parent.exec_cmd(["ssh", self.device.ssh_target, "-t", commands])
            print(output)

            #commands = 'cd ' + self.evolution_path + task.evo_name + '/tren2/Testing/SORN/; screen -dmS ' + task.evo_name + ' sh; screen -S ' + task.evo_name + ' -X stuff "' + cmd + ' ' + task.evo_name + '\r\n"'
            #output = subprocess.run(["ssh", self.ssh_target, "-t", commands], stdout=subprocess.PIPE).stdout.decode('utf-8')
            #print(output)
        except:
            print('execution failed at '+self.device.name)


    def refresh_state(self):
        try:
            #print('refresh state... '+self.device.name+' '+str(self.thread))
            filename = self.device.evolution_path + self.parent.name + '/tren2/Data/Evo/' + get_file_name(self.get_tag(), self.individual, self.thread)
            if self.device.ssh_target == 'local':
                output = self.parent.exec_cmd(['type', filename.replace('/','\\')])#windows
            else:
                commands = "cat "+filename
                output = self.parent.exec_cmd(["ssh", self.device.ssh_target, "-t", commands])#linux
            #print(output)

            if 'score:' in output:
                self.result = float(output.split(':')[1])
        except:
            print('refresh failed for '+self.device.name)

    def is_finished(self):
        return self.result is not None


class Computing_Device():

    def __init__(self, name, ssh_target, command_wrapper, evolution_path, use_screen, cores, python_command='python3', open_command='cat', command_separator=';'):
        self.name = name
        self.ssh_target = ssh_target  #local / vieth@poppy.fias.uni-frankfurt.de
        self.command_wrapper = command_wrapper#srun ...
        self.evolution_path = evolution_path #C:/.../Programmieren/Evolution/ or /Documents/
        self.use_screen = use_screen
        self.cores=cores

        self.python_command=python_command
        self.open_command=open_command
        self.command_separator=command_separator

        self.running_instances=[]


default_devices=[]

#default_devices.append(Computing_Device(name='XPS-Ubuntu',
#                                   ssh_target='marius@127.0.0.1',
#                                   command_wrapper='',
#                                   evolution_path='Evolution/',
#                                   use_screen=True,
#                                   cores=1))

default_devices.append(Computing_Device(name='BV-Server',
                                   ssh_target='marius@hey3kmuagjunsk2b.myfritz.net',
                                   command_wrapper='',
                                   evolution_path='Evolution/',
                                   use_screen=True,
                                   cores=4))

default_devices.append(Computing_Device(name='Poppy',
                                   ssh_target='vieth@poppy.fias.uni-frankfurt.de',
                                   command_wrapper='',
                                   evolution_path='Evolution_Poppy/',
                                   use_screen=True,
                                   cores=4))

default_devices.append(Computing_Device(name='XMEN_1',
                                   ssh_target='vieth@poppy.fias.uni-frankfurt.de',
                                   command_wrapper='srun --partition=x-men --mem=1000 --cpus-per-task=1 ', #specify node
                                   evolution_path='Evolution_XMEN_1/',
                                   use_screen=True,
                                   cores=4))

'''
default_devices.append(Computing_Device(name='Sleuths',
                                   ssh_target='vieth@poppy.fias.uni-frankfurt.de',
                                   command_wrapper='srun --partition=sleuths --reservation triesch-shared --mem=1000 --cpus-per-task=1 ',
                                   evolution_path='Evolution_sleuth/',
                                   use_screen=True,
                                   cores=4))



default_devices.append(Computing_Device(name='XMEN_2',
                                   ssh_target='vieth@poppy.fias.uni-frankfurt.de',
                                   command_wrapper='srun --partition=x-men --mem=1000 --cpus-per-task=1 ', #specify node
                                   evolution_path='Evolution_XMEN_2/',
                                   use_screen=True,
                                   cores=4))

default_devices.append(Computing_Device(name='XMEN_3',
                                   ssh_target='vieth@poppy.fias.uni-frankfurt.de',
                                   command_wrapper='srun --partition=x-men --mem=1000 --cpus-per-task=1 ', #specify node
                                   evolution_path='Evolution_XMEN_3/',
                                   use_screen=True,
                                   cores=4))

default_devices.append(Computing_Device(name='XMEN_4',
                                   ssh_target='vieth@poppy.fias.uni-frankfurt.de',
                                   command_wrapper='srun --partition=x-men --mem=1000 --cpus-per-task=1 ', #specify node
                                   evolution_path='Evolution_XMEN_4/',
                                   use_screen=True,
                                   cores=4))
'''

class Distributed_Evolution(Evolution):

    def __init__(self, evaluation_path, evaluation_file, max_individual_count, generations=None, devices=default_devices, name='Evolution', mutation=0.1, constraints=[], death_rate=0.5):
        super().__init__(None, max_individual_count, generations, name, mutation=mutation, constraints=constraints, death_rate=death_rate)

        self.evaluation_path = evaluation_path
        self.evaluation_file = evaluation_file
        self.devices=devices


        #self.name = 'My_Evo_6543'
        #self.sync()

    def sync(self):

        #git push_to_devices
        self.push_to_git(self.name)

        for device in self.devices:
            print('syncing to '+device.name+'...')
            self.pull_to_device(device, self.name)

    def refresh_states(self):
        for device in self.devices:
            for instance in device.running_instances:
                instance.refresh_state()

    def get_str_indices(self, a):
        result=[]
        for i, val in enumerate(a):
            if type(val)==str:
                result.append(i)
        return result


    def get_fitnesses(self, living_individuals):
        fitnesses = [None for _ in living_individuals]

        while None in fitnesses or len(self.get_str_indices(fitnesses))>0:

            #refresh
            self.refresh_states()

            #get and clear finished
            for device in self.devices:
                remove_instances=[]
                for instance in device.running_instances:

                    if instance.is_finished():
                        index = living_individuals.index(instance.individual)
                        fitnesses[index] = instance.result
                        #print('new score received '+str(instance.result)+' '+str(instance.individual))
                        instance.terminate()
                        remove_instances.append(instance)

                device.running_instances=[inst for inst in device.running_instances if inst not in remove_instances]

            #start_new
            for device in self.devices:
                for i in range(device.cores-len(device.running_instances)):

                    index = None

                    if None in fitnesses:
                        index = fitnesses.index(None)
                    else:
                        indices=self.get_str_indices(fitnesses)
                        if len(indices)>0:
                            index = random.choice(indices)#todo:choose randomly?

                    if index is not None:
                        instance = Execution_Instance(device, living_individuals[index], self)
                        #print('started:',i,'thread num:',instance.thread)
                        instance.execute()
                        device.running_instances.append(instance)
                        if fitnesses[index] is None:
                            fitnesses[index]=''
                        fitnesses[index]+=device.name

            print(fitnesses)
            time.sleep(60)

        #terminate all left
        for device in self.devices:
            for instance in device.running_instances:
                instance.terminate()
            device.running_instances.clear()

        return fitnesses



    def exec_cmd(self, cmd, timeout=5, shell=False):
        #print(cmd)
        return subprocess.run(cmd, stdout=subprocess.PIPE, shell=shell, stderr=subprocess.DEVNULL, timeout=timeout).stdout.decode('utf-8')  # shell???

    def push_to_git(self, evolution_name):
        #push
        output = self.exec_cmd('cd ../../ && git add . && git commit -m "'+evolution_name+'" && git push',timeout=None, shell=True)
        print(output)

    def pull_to_device(self, device, evolution_name):

        #pull
        commands = "cd "+device.evolution_path+"; mkdir "+self.name+"; cd "+self.name+"; git clone git@gitlab.com:MariusVieth/tren2.git --depth=1"
        output = self.exec_cmd(["ssh", device.ssh_target, "-t", commands],timeout=None)#"vieth@poppy.fias.uni-frankfurt.de"
        print(output)

        #print(device.name, 'success')


if __name__ == '__main__':
    individuals = [
        [0.13789816792067938, 0.17065514066367593, 0.11168320620611354, 0.16840806786309856, 1.4946513397198866,
         0.079921908822618, 0.29510107972754973, 0.0009600193439867156, 0.9270729711297467, 0.7566773088420518,
         0.8725072548532814, 0.7767435098374641, 0.048701872452675085, 0.05184909253434595],
        [0.1369393011871059, 0.16320512081448846, 0.10828724646304186, 0.17549197504964528, 1.4977178445693171,
         0.07770609994022251, 0.29912106127472526, 0.000987033275365088, 0.9460518633185139, 0.7757587402776814,
         0.8903230183657246, 0.8346380786772245, 0.04809033404857177, 0.049561074187045265],
        [0.13826552278293702, 0.17015234576503943, 0.11169084906592291, 0.16923287064556833, 1.4836054232886746,
         0.08076207798242323, 0.29091573541657195, 0.0009543949166515931, 0.9617821583083058, 0.7479971234488287,
         0.8636616593517366, 0.7709186293623992, 0.047495907589052214, 0.05239282086830213],
        [0.13661961018756388, 0.1662884856434496, 0.1107623153127642, 0.17214343077038996, 1.4478999371156194,
         0.08031041021644648, 0.2980375173501598, 0.000952421287982886, 0.8611936274038073, 0.789858704510338,
         0.9079284773280789, 0.8160644059883645, 0.05125191522785646, 0.0489368673851671],
        [0.12975862117794404, 0.17025462839183017, 0.11128076164970184, 0.16563202274292443, 1.5054116783654887,
         0.0801396367575215, 0.29193566635507795, 0.0009142581111154673, 0.9172289667708686, 0.762672130984394,
         0.8763206679453999, 0.8084695496310645, 0.0519385634336421, 0.04906493868102084],
        [0.1367180072966108, 0.17082486427168236, 0.10937367735190918, 0.17702383903765637, 1.5066677824525254,
         0.08012465009721595, 0.3050036156389453, 0.0009366419468003736, 0.8660554744230655, 0.8076295345479414,
         0.8699292108255529, 0.8132807942323248, 0.049566460381698416, 0.05241213929544708],
        [0.1319125082444357, 0.16501895955623347, 0.1115570859200819, 0.17455039644413317, 1.5244500435387216,
         0.08611113843309873, 0.2932413509043705, 0.0009773092905971772, 0.9159156903442719, 0.7672297857248398,
         0.8605770889417345, 0.7940705116108155, 0.048209099527375794, 0.049865020440248285],
        [0.1267201379419818, 0.16594913349384444, 0.11083365181334674, 0.16541162822952898, 1.4658562886745967,
         0.08172444660034578, 0.29104319495091396, 0.0009119603589200016, 0.9051060160008418, 0.7806250438123724,
         0.9094333321706622, 0.7964744568527374, 0.050458386585313666, 0.04841185518369756],
        [0.13943896190808058, 0.17407481135977426, 0.11010244307846394, 0.1727974369836428, 1.557006111147047,
         0.07958801718988902, 0.29442912535312254, 0.0009679962126765122, 0.9371515180914547, 0.7904779585284682,
         0.8621109817422786, 0.776567027914515, 0.04928355380171231, 0.05063461904304101],
        [0.13292907280771982, 0.1647564781215282, 0.10938451792083152, 0.17451585753584603, 1.5036131775711774,
         0.08060475707463866, 0.29756734274023966, 0.0009974469644896578, 0.8909929653973142, 0.7962882851935996,
         0.8667356121393888, 0.7876101041540522, 0.04757841320045718, 0.04859724532660686],
        [0.1390985775251823, 0.17248600112592086, 0.11242240675043771, 0.17113098039211955, 1.4741119430445853,
         0.07850089995519846, 0.2779914796270492, 0.0009339739625524561, 0.9679865482333263, 0.7550483510232994,
         0.8626403638891458, 0.7624466810882977, 0.04736905492031667, 0.052435655008812546],
        [0.1345878212208438, 0.16970350465000092, 0.10856544298212631, 0.17346400727495584, 1.5782472787923294,
         0.08207694501758396, 0.30229518866779465, 0.0009665660445950586, 0.8945030978067753, 0.7956373964169333,
         0.8585063436332135, 0.7892246549246438, 0.04912086326521122, 0.04993707278062062],
        [0.1388752541978183, 0.16979581183593975, 0.11103395144206898, 0.17025640025544708, 1.4648678613975854,
         0.08181670734594748, 0.29342076212098345, 0.0009553195931995628, 0.9240313711288549, 0.7663740744078534,
         0.8787417944784155, 0.7887901757470802, 0.048341900888022316, 0.0529289498138576],
        [0.13846323574824465, 0.17000184217540124, 0.11198759522288722, 0.17282226127385722, 1.4963893657941332,
         0.07891091498195449, 0.297405771370286, 0.0009559395108863506, 0.9182661600037596, 0.7672508767913827,
         0.8666386541188165, 0.7955913516742491, 0.052450156228847675, 0.05254415803168709],
        [0.13128518931324898, 0.16278705028191157, 0.11184457433786225, 0.1727517669342289, 1.5433184118704595,
         0.08280934450433311, 0.29371918154407245, 0.0009753526207699803, 0.9262282843141727, 0.7652824561723829,
         0.8659643290543815, 0.7798099454456108, 0.04768267106134955, 0.04875748832693371],
        [0.12455355410846979, 0.17054076692730202, 0.10851507773791176, 0.1755155102556199, 1.4989090864144479,
         0.08600724396255803, 0.3038974915487612, 0.0009382872552383427, 0.8620229181478204, 0.8016962019635222,
         0.8758053904549297, 0.7716321748851126, 0.04979495011516467, 0.05134834059069857]]

    #individuals=[[1,2,3]]

    #'Exploration/Evolution/'
    #'X_test_evo.py'

    de = Distributed_Evolution(evaluation_path='Testing/SORN/', evaluation_file='GrammarExperiment_New.py', max_individual_count=32, devices=default_devices, name='My_Evo_multi_device', mutation=0.1, constraints=[], death_rate=0.5)
    de.sync()
    de.start(individuals)

