import random

import sys
import os
import threading

from Exploration.StorageManager.StorageManager import *


def string_to_array(s):
    s=s.replace(' ','')
    result = []
    s = s.replace(']', '')
    parts = s.split('[')
    for p in parts:
        if p != '':
            result.append([float(num) for num in p.split(',') if num != ''])
    return result

class Individual:
    def __init__(self, params, lifetime=0):
        self.parameters = params
        self.fitness = -1
        self.lifetime = lifetime



class Evolution:
    def __init__(self, evaluation_function, max_individual_count, generations=None, name='Evolution', mutation = 0.1, constraints=[], death_rate=0.5, param={}):
        self.datafolder=get_data_folder()+'/Evo/'

        if not os.path.exists(self.datafolder):
            try:
                os.mkdir(self.datafolder)
            except:
                print('evolution folder already exits')

        self.name = name#+'_{}'.format(int(np.random.rand()*10000))
        #print(self.name)
        self.param=param
        self.savestate = True
        self.evaluation_function = evaluation_function
        self.max_individual_count = max_individual_count
        self.generations = generations
        self.individuals = []
        self.mutation = mutation
        self.constraints = constraints
        self.death_rate = death_rate
        self.plot_progress=False
        self.paused=False


    def breed(self):

        new_ind = []

        weights = np.array(self.set_get_ind_params("lifetime")).copy()
        #weights -= min(weights)
        weights = weights / np.sum(weights)



        for _ in range(self.max_individual_count-len(self.individuals)):

            parent1 = np.random.choice(self.individuals, 1, p=weights)[0]
            parent2 = np.random.choice(self.individuals, 1, p=weights)[0]

            ind = [] #new individuals
            for p_i in range(len(parent1.parameters)):
                p1 = np.clip(np.random.normal(parent1.parameters[p_i], parent1.parameters[p_i]*self.mutation), 0, None)
                p2 = np.clip(np.random.normal(parent2.parameters[p_i], parent2.parameters[p_i]*self.mutation), 0, None)
                ind.append(random.choice([p1, p2]))

            for constraint in self.constraints:
                exec(constraint)

            new_ind.append(Individual(ind))

        self.individuals += new_ind

    def natural_selection(self):

        kill_count = int(len(self.individuals)*self.death_rate)

        for _ in range(kill_count):
            kill_ind = self.individuals[0]
            for ind in self.individuals:
                if ind.fitness < kill_ind.fitness:
                    kill_ind = ind

            self.individuals.remove(kill_ind)

    def set_get_ind_params(self, attr, values=None):
        result = []
        for i, ind in enumerate(self.individuals):
            if values is not None and i < len(values):
                setattr(ind, attr, values[i])
            result.append(getattr(ind, attr))
        return result


    def get_fitnesses(self, living_individuals):
        return [self.evaluation_function(self.name, individual, self.param) for individual in living_individuals]



    def start(self, seed_individuals):
        #self.start_input_thread()
        self.individuals.clear()

        generation = 0

        self.save('Seed:', seed_individuals)
        for ind in seed_individuals:

            for constraint in self.constraints:
                exec(constraint)

            self.individuals.append(Individual(ind, 1))

        self.breed()
        self.save('Start:', self.set_get_ind_params('parameters'))

        while self.generations is None or generation < self.generations:

            while self.paused:
                print('paused...')
                time.sleep(10)

            generation += 1

            fitnesses = self.get_fitnesses(self.set_get_ind_params('parameters'))
            self.set_get_ind_params('fitness', fitnesses)

            #if self.plot_progress:
            #    plt.plot(np.zeros(len(fitnesses))+generation, fitnesses)
            #    plt.show()

            new_lt = (np.array(self.set_get_ind_params('lifetime'))+np.array(self.set_get_ind_params('fitness', fitnesses)))/2
            self.set_get_ind_params('lifetime', new_lt)


            self.natural_selection()
            self.save('Gen {} survivers:'.format(generation), self.set_get_ind_params('parameters'))
            self.save('Gen {} fitnesses:'.format(generation), self.set_get_ind_params('fitness'))
            self.save('Gen {} lifetime:'.format(generation), self.set_get_ind_params('lifetime'))
            self.breed()
            self.save('Gen {} breed:'.format(generation), self.set_get_ind_params('parameters'))


    def get_evo_file(self):
        return self.datafolder+self.name+".txt"

    def evo_file_exists(self):
        return os.path.exists(self.get_evo_file())

    def save(self, message, data):
        print(message, data)
        if self.savestate:
            f = open(self.get_evo_file(), "a")
            f.write(message+" {}".format(data)+"\n")
            f.close()




    def continue_evo(self, file):
        f = open(self.datafolder+file, "r")
        population = None
        for line in f.readlines():
            if 'survivers:' in line:
                population=string_to_array(line[line.index('['):-1])
                print(population)
        f.close()

        if population is not None:
            name=file.split('.')[0]
            print('setting target file to '+name)
            self.name = name
            print('starting evolution...')
            self.save('Continue...', population)
            self.start(population)
        else:
            print('no individuals found')

    #add history saving
    #plot progress in UI Window
    #add plot and dim reduction

    def start_input_thread(self):

        def input_collect_function():
            while True:
                for line in sys.stdin:
                    if line and line != '\n':
                        line=line.replace('\r', '').replace('\n', '')
                        if '[' in line and ']' in line:
                            print('adding individual(s)...')
                            genes = string_to_array(line)
                            for gene in genes:
                                if len(self.individuals[0].parameters) == len(gene):
                                    ind = Individual(genes)
                                    ind.fitness = np.max(self.set_get_ind_params('fitness'))
                                    ind.lifetime = np.max(self.set_get_ind_params('lifetime'))
                                    self.individuals.append(ind)
                                    print('Individial added:', gene)
                                else:
                                    print('wrong number of genes in', gene)
                        elif 'pause' in line:
                            self.paused = True
                            print('evolution stopped')
                        elif 'start' in line:
                            self.paused = False
                            print('evolution continued')
                        elif line.isdigit():
                            if hasattr(self,'thread_count'):
                                self.thread_count=int(line)
                                print('thread count set to ' + line)
                        elif line.replace('.','').isdigit():
                            self.mutation=float(line)
                            print('mutation rate set to', line)
                        else:
                            print('unknown command' + line)
                time.sleep(1)

        threading.Thread(target=input_collect_function).start()
