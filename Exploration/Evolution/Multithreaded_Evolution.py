import sys
sys.path.append('../../')

from Exploration.Evolution.Evolution import *
from multiprocessing import Process, Queue


#def test(individual_pipeline, fitness_pipeline):
#    while True:
#        if fitness_pipeline.empty() and not individual_pipeline.empty():
#            individual = individual_pipeline.get()
#            fitness = 10
#            fitness_pipeline.put((fitness, individual))

def multithreading_evaluation_func_wrapper(eval_f, tag, individual_pipeline, param, fitness_pipeline):
    # TODO: test
    try:
        import psutil as psu
        parent = psu.Process()
        parent.nice(psu.BELOW_NORMAL_PRIORITY_CLASS)
    except:
        print('not able to set BELOW_NORMAL_PRIORITY_CLASS')

    while True:
        if fitness_pipeline.empty() and not individual_pipeline.empty():
            individual = individual_pipeline.get()
            fitness = eval_f(tag, individual, param)
            fitness_pipeline.put([fitness, individual])

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
        individual_pipeline = Queue()
        fitness_pipeline = Queue()
        p = Process(target=multithreading_evaluation_func_wrapper, args=(self.evaluation_function, self.name, individual_pipeline, self.param, fitness_pipeline))
        p.start()
        self.rendering_threads.append(p)
        self.individual_pipelines.append(individual_pipeline)
        self.fitness_pipelines.append(fitness_pipeline)

    def remove_process(self):
        p = self.rendering_threads.pop()
        p.terminate()
        self.individual_pipelines.pop()
        self.fitness_pipelines.pop()

    def adjust_process_count(self):
        for _ in range(len(self.rendering_threads) - self.thread_count):
            self.add_process()

        for _ in range(self.thread_count - len(self.rendering_threads)):
            self.remove_process()


    def __init__(self, evaluation_function, max_individual_count, generations=None, thread_count=1, name='Evolution', mutation=0.1, constraints=[], death_rate=0.5, param={}):
        super().__init__(evaluation_function, max_individual_count, generations, name, mutation=mutation, constraints=constraints, death_rate=death_rate, param=param)

        self.rendering_threads = []
        self.individual_pipelines = []
        self.fitness_pipelines = []

        self.thread_count = thread_count

        for t_i in range(self.thread_count):
            self.add_process()


    def get_fitnesses(self, living_individuals):

        self.adjust_process_count()

        fitnesses = [None for _ in living_individuals]

        while None in fitnesses or -1 in fitnesses:

            for ind, fit in zip(self.individual_pipelines, self.fitness_pipelines):

                if None in fitnesses and fit.empty() and ind.empty():
                    index = fitnesses.index(None)
                    fitnesses[index] = -1
                    individual = living_individuals[index]
                    ind.put(individual)

                if not fit.empty():
                    fitness, individual = fit.get()
                    index = living_individuals.index(individual)
                    fitnesses[index] = fitness
                    print(fitness, individual)

            time.sleep(0.1)

        return fitnesses


if __name__ == '__main__':

    #individuals = [[0.95, 0.4, 0.1383, 0.1698, 0.1, 0.00015, 0.04, 0.2944, 0.0006, 0.2, 0.015, 0.2944, 0.1, 0.0001, 0.87038, 0.82099, 1.5, 0.08, 15.0]]
    individuals = [[39.554, 16.13, 26.068, 20.96, 0.1158, 0.5067, 0.000112073, 0.05369, 0.17177, 0.00030581, 10.836, 0.00533, 0.4372, 0.0491]]#[50.0, 20.0, 20.0, 20.0, 0.1383, 0.5, 0.00015, 0.04, 0.2944, 0.0006, 15.0, 0.015, 0.2944, 0.1]

    constraints = ['ind=np.clip(ind,0.00001,None)']#'ind[0]=np.clip(ind[0],1.0,None)'
    from Testing.SORN_Grammar.Experiment_PV_SOM import *
    evolution = Multithreaded_Evolution(run, 30, thread_count=5, name='som_pv_improvement_15_04_2', mutation=0.05, constraints=constraints, param={'N_e': 900, 'TS':[1]})#new_evo_24_02_20
    evolution.start(individuals)
    #evolution.continue_evo('new_evo_24_02_20_9323_continue_larger.txt')
    #evolution.continue_evo('new_grammar_new_params_16_03_2_8170.txt')
    #evolution.continue_evo('som_pv_test_5293.txt')