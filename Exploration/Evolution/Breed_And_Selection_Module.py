import random
import numpy as np
from PymoNNto.Exploration.Evolution.Interface_Functions import *
from PymoNNto.Exploration.Evolution.Evolution_Individual import *

class Default_Breed_And_Select:

    def __init__(self, parent, death_rate, mutation, individual_count, constraints, additional_evo_params={}):
        self.parent = parent
        self.death_rate = death_rate
        self.mutation = mutation
        self.individual_count = individual_count
        self.generation = 1
        self.constraints = constraints

        if 'no_high_risk_inds' in additional_evo_params:
            self.avoid_high_risk_high_reward_individuals = additional_evo_params['no_high_risk_inds']
        else:
            self.avoid_high_risk_high_reward_individuals = True

        if 're_eval_inds' in additional_evo_params:
            self.re_evaluate_genomes = additional_evo_params['re_eval_inds']
        else:
            self.re_evaluate_genomes = True


    def natural_selection(self, individuals):
        result = individuals.copy()

        #sort (biggest score first)
        for i in range(len(result)-1):
            for j in range(len(result)-i-1):
                if result[i].score < result[i+1+j].score:
                    temp = result[i]
                    result[i] = result[i+1+j]
                    result[i+1+j] = temp

        kill_count = int(len(result) * self.death_rate)
        for _ in range(kill_count):
            result.pop(-1)#remove last (smallest score)

        return result

    def generate_new_generation(self, old_individuals):
        survivours = self.natural_selection(old_individuals)
        new_population = self.breed(survivours)

        self.generation += 1
        for individual in new_population:
            individual.id = self.parent.get_individual_id()

        return new_population


    def update_population(self):
        #print('update...', len(self.parent.non_scored_individuals), len(self.parent.running_individuals), len(self.parent.scored_individuals))
        if len(self.parent.non_scored_individuals) == 0 and len(self.parent.running_individuals) == 0:

            new_population = self.generate_new_generation(self.parent.scored_individuals)

            print('new generation:', self.generation)

            self.parent.non_scored_individuals = new_population
            self.parent.running_individuals = []
            self.parent.scored_individuals = []

            #if not self.re_evaluate_genomes:
            #    for s in survivours:
            #        found = self.parent.find(self.parent.non_scored_individuals, s)
            #        self.parent.non_scored_individuals.remove(found)
            #        self.parent.running_individuals.append(found)

            #        processing_genome = self.parent.add_name_gen_id_inactive_to_genome(s)
            #        set_score(s.score, _genome=processing_genome)#create files #s['score']
            #        self.parent.new_score_event(processing_genome)#move from non_scored_individuals to scored_individuals



    def get_offspring(self, ind1, ind2):
        child = Evolution_individual(genome=None)

        while not child.is_valid_genome(self.constraints):
            child.genome = {}

            for key in ind1.genome.keys():
                if key in ind2.genome.keys():
                    g1 = np.random.normal(ind1.genome[key], np.clip(ind1.genome[key] * self.mutation, 0, None))
                    g2 = np.random.normal(ind2.genome[key], np.clip(ind2.genome[key] * self.mutation, 0, None))
                    child.genome[key] = random.choice([g1, g2])
                else:
                    print('not the same genes', ind1, ind2)

        return child


    def breed(self, individuals):

        #weights are used to avoid high risk, high reward individuals.
        #only individuals with persistent performances over generations have high mate_chance and produce offspring
        weights = np.ones(len(individuals))
        if self.avoid_high_risk_high_reward_individuals:
            for i, ind in enumerate(individuals):
                if ind.mate_chance is None or ind.score is None:#score is none during initialization
                    ind.mate_chance = 1
                else:
                    ind.mate_chance = (ind.mate_chance + ind.score) / 2
                weights[i] = ind.mate_chance
        weights = weights / np.sum(weights)  # todo divide by zero for negative scores!


        result = []

        for ind in individuals:
            result.append(ind.get_copy())# only genome and mate_chances are copied

        new_count = self.individual_count - len(result)

        for i in range(new_count):
            parent1 = np.random.choice(individuals, 1, p=weights)[0]
            parent2 = np.random.choice(individuals, 1, p=weights)[0]
            result.append(self.get_offspring(parent1, parent2))

        return result

