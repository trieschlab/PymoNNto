import sys
sys.path.append('../../')

from Exploration.Evolution.Evolution import *
from multiprocessing import Process, Queue, Pipe
import Exploration.Evolution.Computing_Devices as comp_dev
import subprocess
import time
import os

#def test(individual_pipeline, fitness_pipeline):
#    while True:
#        if fitness_pipeline.empty() and not individual_pipeline.empty():
#            individual = individual_pipeline.get()
#            fitness = 10
#            fitness_pipeline.put((fitness, individual))

def multithreading_evaluation_func_wrapper(import_file, func_name, param, conn):
    try:
        import psutil as psu
        parent = psu.Process()
        parent.nice(psu.BELOW_NORMAL_PRIORITY_CLASS)
    except:
        print('not able to set BELOW_NORMAL_PRIORITY_CLASS')

    exec('import ' + import_file + ' as target')
    eval_f = eval('target.'+func_name)

    while True:

        if conn.poll():
            individual=conn.recv()
            #try:
            param['ind']=individual
            #print(param)
            fitness = eval_f(attrs=param)
            conn.send([fitness, individual])
            #except:
            #    conn.send([None, individual])

        conn.send('ready')
        time.sleep(1.0)



def remote_evaluation_func_wrapper(device, import_file, func_name, tag, param, conn):

    while True:
        if conn.poll():
            individual = conn.recv()
            #try:

            ident=str(np.random.rand()).split('.')[1]

            pexec = 'python3 exec.py '+ident+' '+str(individual).replace(' ', '')+' '+import_file+' '+func_name+''
            if hasattr(device, 'slurm_wrapper'):
                pexec = device.slurm_wrapper.replace('*command*', 'srun') + ' --job-name=' + tag + ' '+pexec
            for k, v in param.items():
                pexec += ' '+k+'='+str(v).replace(' ', '')
            cmd = 'cd '+device.main_path+tag+'/Exploration/Evolution/; screen -dmS ' + ident + ' sh; screen -S ' + ident + ' -X stuff "' + pexec + ' \r\n"'
            cmd = device.ssh_wrap_cmd(cmd)

            subprocess.run(cmd)
            time.sleep(1)

            while True:
                dst = '../../Data/evo/' + ident + '.txt'
                src = device.ssh_target + ':' + device.main_path+tag+'/Data/Evo/'+ident+'.txt'
                scp_cmd='scp ' + src + ' ' + dst

                subprocess.run(scp_cmd)

                if os.path.isfile(dst):
                    fitness = float(open(dst, 'r').read().split(' ')[-1])
                    conn.send([fitness, individual])
                    break
                else:
                    print('not found')
                    time.sleep(10)
                #else:
                #    conn.send([None, individual])
            #print('out', output)
            #fitness = output.split(' ')[-1].replace('\r', '').replace('\n', '')
            #if fitness.replace('.', '').isnumeric():
            #    fitness = float(fitness)
            #else:
            #    fitness = None
            #conn.send([fitness, individual])
            #except:
            #    conn.send([None, individual])

        conn.send('ready')
        time.sleep(1.0)


def run_multiple_times(function, num_threads, args=[]):
    if num_threads == -1:
        function(args)#todo args???
    else:
        result = []
        for i in range(num_threads):
            p = Process(target=function, args=args)
            p.start()
            result.append(p)
        return p

class Multithreaded_Evolution(Evolution):

    def add_process(self):
        #individual_pipeline = Queue()
        #fitness_pipeline = Queue()
        parent_conn, child_conn = Pipe()
        p = Process(target=multithreading_evaluation_func_wrapper, args=(self.import_file, self.func_name, self.param, child_conn))
        p.pipe_conn = parent_conn
        p.start()
        self.rendering_threads.append(p)
        #self.individual_pipelines.append(individual_pipeline)
        #self.fitness_pipelines.append(fitness_pipeline)

    #def remove_process(self):
    #    p = self.rendering_threads.pop()
    #    p.terminate()
    #    self.individual_pipelines.pop()
    #    self.fitness_pipelines.pop()

    def add_remote_process(self, device):
        #remote_individual_pipeline = Queue()
        #remote_fitness_pipeline = Queue()
        parent_conn, child_conn = Pipe()
        p = Process(target=remote_evaluation_func_wrapper, args=(device, self.import_file, self.func_name, self.name, self.param, child_conn))
        p.pipe_conn = parent_conn
        p.start()
        self.remote_rendering_threads.append(p)
        #self.remote_individual_pipelines.append(remote_individual_pipeline)
        #self.remote_fitness_pipelines.append(remote_fitness_pipeline)

    #def adjust_process_count(self):
    #    for _ in range(len(self.rendering_threads) - self.thread_count):
    #        self.add_process()#

    #    for _ in range(self.thread_count - len(self.rendering_threads)):
    #        self.remove_process()


    def __init__(self, import_file, func_name, max_individual_count, generations=None, thread_count=1, name='Evolution', mutation=0.1, constraints=[], death_rate=0.5, param={}, distributed=False):
        #exec('from ' + import_file + ' import *')

        self.import_file = import_file
        self.func_name = func_name

        super().__init__(None, max_individual_count, generations, name, mutation=mutation, constraints=constraints, death_rate=death_rate, param=param)

        self.rendering_threads = []
        #self.individual_pipelines = []
        #self.fitness_pipelines = []

        self.thread_count = thread_count

        for t_i in range(self.thread_count):
            self.add_process()

        #self.remote_rendering_threads = []
        #self.remote_individual_pipelines = []
        #self.remote_fitness_pipelines = []

        #if distributed:
        #    for dev in comp_dev.get_devices(local=False):
        #        self.add_remote_process(dev)
        #    #self.my_devices=comp_dev.get_devices(local=False)
        #    #for dev in self.my_devices:
        #    #    dev.process=None


    def get_fitnesses(self, living_individuals):
        print()
        last_progress=-1

        #self.adjust_process_count()

        fitnesses = [None for _ in living_individuals]

        while None in fitnesses or -1 in fitnesses or -2 in fitnesses:

            for thread in self.rendering_threads:

                ready = False
                data = None
                while thread.pipe_conn.poll():
                    read = thread.pipe_conn.recv()
                    if read == 'ready':
                        ready = True
                    else:
                        data = read

                if ready:
                    if None in fitnesses:
                        index = fitnesses.index(None)
                        fitnesses[index] = -1
                        individual = living_individuals[index]
                        thread.pipe_conn.send(individual)
                    elif -2 in fitnesses:
                        index = fitnesses.index(-2)
                        fitnesses[index] = -1
                        individual = living_individuals[index]
                        thread.pipe_conn.send(individual)

                if data is not None:
                    fitness, individual = data
                    if individual in living_individuals:
                        index = living_individuals.index(individual)
                        fitnesses[index] = fitness
                        print(fitness, individual)

                time.sleep(0.1)

            #print(fitnesses)
            current_progress = sum([1 for i in fitnesses if i is not None and i>=0])/len(fitnesses)
            if current_progress != last_progress:
                print('\rprogress: '+str(current_progress)+'%', end='')
                last_progress = current_progress
            time.sleep(1.0)  # 0.1

        return fitnesses

        '''
                    for thread in self.remote_rendering_threads:

                ready = False
                data = None
                while thread.pipe_conn.poll():
                    read = thread.pipe_conn.recv()

                    if read == 'ready':
                        ready = True
                    else:
                        data = read

                print(ready, data)

                if ready:
                    if None in fitnesses:
                        index = fitnesses.index(None)
                        fitnesses[index] = -2
                        individual = living_individuals[index]
                        thread.pipe_conn.send(individual)

                if data is not None:
                    fitness, individual = data
                    if individual in living_individuals:
                        index = living_individuals.index(individual)
                        fitnesses[index] = fitness
                        #print(fitness, individual)
        

                    '''

        '''
        for dev in self.my_devices:
            if dev.process is None:
                if None in fitnesses:
                    index = fitnesses.index(None)
                    fitnesses[index] = -2
                    individual = living_individuals[index]
                    #execute
                    pexec = 'python3 exec.py ' + self.name + ' ' + str(individual).replace(' ','') + ' ' + import_file + ' ' + self.func_name
                    if hasattr(dev, 'slurm_wrapper'):
                        pexec = dev.slurm_wrapper.replace('*command*','srun') + ' --job-name=' + self.name + ' ' + pexec
                    for k, v in self.param.items():
                        pexec += ' ' + k + '=' + str(v).replace(' ', '')
                    cmd = dev.ssh_wrap_cmd('cd ' + dev.main_path + self.name + '/Exploration/Evolution/; ' + pexec)
                    print(cmd)
                    dev.current_individual=individual
                    dev.process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                    dev.process.wait()
            else:
                poll = dev.process.poll()
                print(poll)
                if poll is not None and poll <= 0:#finished
                    try:
                        output, error = dev.process.communicate(timeout=15)
                        print(output, error)
                        output = output.decode('utf-8')
                        fitness = output.split(' ')[-1].replace('\r', '').replace('\n', '')
                        if fitness.replace('.', '').isnumeric():
                            fitness = float(fitness)
                            index = living_individuals.index(dev.current_individual)
                            fitnesses[index] = fitness
                        else:
                            fitnesses[index] = None
                    except:
                        fitnesses[index] = None

                    dev.process = None
         '''

        '''
            for ind, fit in zip(self.individual_pipelines, self.fitness_pipelines):

                while not fit.empty():
                    fitness, individual = fit.get()
                    index = living_individuals.index(individual)
                    fitnesses[index] = fitness
                    print(fitness, individual)

                if ind.empty():
                    if None in fitnesses:#first execute new individuals
                        index = fitnesses.index(None)
                        fitnesses[index] = -1
                        individual = living_individuals[index]
                        ind.put(individual, block=False)
                    elif -2 in fitnesses:#when there are no new individuals => evaluate remote individuals in case some remote source failed
                        index = fitnesses.index(-2)
                        fitnesses[index] = -1
                        individual = living_individuals[index]
                        ind.put(individual, block=False)
                        
            time.sleep(0.1)
        '''





        '''
            for ind, fit in zip(self.remote_individual_pipelines, self.remote_fitness_pipelines):

                while not fit.empty():
                    fitness, individual = fit.get()
                    index = living_individuals.index(individual)
                    fitnesses[index] = fitness
                    print(fitness, individual)

                if ind.empty():
                    if None in fitnesses:
                        index = fitnesses.index(None)
                        fitnesses[index] = -2
                        individual = living_individuals[index]
                        ind.put(individual, block=False)

                time.sleep(0.1)
        '''









def args_to_param_dict(add=[]):
    result = {}
    for arg in add+sys.argv[1:]:
        split = arg.split('=')
        if len(split) == 2:
            key, value  =split
            try:
                result[key] = eval(value)
            except:
                result[key] = value
        else:
            print('unknown parameter', arg)
    return result




if __name__ == '__main__':




    '''
    if len(sys.argv) > 1:
        evo_name = sys.argv[1]
    else:
        evo_name = 'evz'

    if len(sys.argv) > 2:
        individuals = sys.argv[2]
    else:
        individuals = '[[0.95, 0.4, 0.1383, 0.1698, 0.1, 0.00015, 0.04, 0.2944, 0.0006, 0.5, 0.015, 0.2944, 0.1, 0.0001, 0.87038, 0.82099, 1.5, 0.08, 15.0]]'

    if len(sys.argv) > 3:
        import_file = sys.argv[3]
    else:
        import_file = 'Testing.SORN_Grammar.GrammarExperiment_Hierarchical'

    #if len(sys.argv)>3:
    #    constraints = sys.argv[4]
    #else:
    #    constraints = "['ind=np.clip(ind,0.00001,None)']"

    if len(sys.argv) > 4:
        mutation = sys.argv[4]
    else:
        mutation = "0.05"

    if len(sys.argv) > 5:
        distributed = eval(sys.argv[5])
    else:
        distributed = True

    params = {'evolution':True}
    if len(sys.argv) > 6:
        for arg in sys.argv[6:]:
            if '=' in arg:
                key, value = arg.split('=')
                params[key] = eval(value)
            else:
                print('no = in argument! (ignored)')
    else:
        params['N_e'] = 900
        params['TS'] = [1]
    


    print(individuals)
    individuals = eval(individuals)
    if type(individuals[0]) is not list:
        individuals = [individuals]
    '''

    params = args_to_param_dict(['name=default_evo_name','evolution=True', 'N_e=900', 'TS=[1]', 'print=False'])

    name = params.get('name', None)
    import_file = params.get('import_file', 'Testing.SORN_Grammar.GrammarExperiment_Hierarchical')
    mutation = params.get('mutation', 0.05)
    distributed = params.get('distributed', False)
    max_individual_count = params.get('max_individual_count', 30)
    thread_count = params.get('thread_count', 4)
    func_name = params.get('func_name', 'run')
    individuals = params.get('individuals',[[0.95, 0.4, 0.1383, 0.1698, 0.1, 0.00015, 0.04, 0.2944, 0.0006, 0.5, 0.015, 0.2944, 0.1, 0.0001, 0.87038, 0.82099, 1.5, 0.08, 15.0]])
    if type(individuals[0]) is not list:
        individuals = [individuals]

    evolution = Multithreaded_Evolution(import_file=import_file, func_name=func_name, max_individual_count=max_individual_count, thread_count=thread_count, name=name, mutation=mutation, constraints=['ind=np.clip(ind,0.00001,None)'], distributed=distributed, param=params)

    if evolution.evo_file_exists():
        evolution.continue_evo(name+'.txt')
    else:
        evolution.start(individuals)



    # individuals = [[0.95, 0.4, 0.1383, 0.1698, 0.1, 0.00015, 0.04, 0.2944, 0.0006, 0.2, 0.015, 0.2944, 0.1, 0.0001, 0.87038, 0.82099, 1.5, 0.08, 15.0]]
    # [[39.554, 16.13, 26.068, 20.96, 0.1158, 0.5067, 0.000112073, 0.05369, 0.17177, 0.00030581, 10.836, 0.00533, 0.4372, 0.0491]]#[50.0, 20.0, 20.0, 20.0, 0.1383, 0.5, 0.00015, 0.04, 0.2944, 0.0006, 15.0, 0.015, 0.2944, 0.1]
    #evolution.continue_evo('new_evo_24_02_20_9323_continue_larger.txt')
    #evolution.continue_evo('new_grammar_new_params_16_03_2_8170.txt')
    #evolution.continue_evo('som_pv_test_5293.txt')