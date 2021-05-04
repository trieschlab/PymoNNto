import random
import numpy as np

class Default_Breed_And_Select:

    def __init__(self, parent, death_rate, mutation, individual_count, constraints, avoid_high_risk_high_reward_individuals=True):
        self.parent = parent
        self.death_rate = death_rate
        self.mutation = mutation
        self.individual_count = individual_count
        self.generation = 1
        self.constraints = constraints
        self.avoid_high_risk_high_reward_individuals=avoid_high_risk_high_reward_individuals

    def update_population(self):
        if len(self.parent.non_scored_individuals) == 0 and len(self.parent.running_individuals) == 0:

            survivours = self.natural_selection(self.parent.scored_individuals)

            if self.avoid_high_risk_high_reward_individuals:
                for s in survivours:# improve breed chance for older individuals (avoid high risk, high reward population)
                    bc = 1
                    if 'mate_chance' in s:
                        bc = s['mate_chance']
                    s['mate_chance'] = (bc+s['score'])/2

            new_population = self.breed(survivours)

            for p in new_population:#remove scores
                if 'score' in p:
                    p.pop('score')
            #optional: do not re-score individuals => put old individuals in "scored"

            print('new gen breeding... survivours', survivours)

            self.parent.non_scored_individuals = new_population.copy()
            self.parent.running_individuals = []
            self.parent.scored_individuals = []
            self.generation += 1

    def natural_selection(self, individuals):
        result = individuals.copy()
        kill_count = int(len(result) * self.death_rate)

        for _ in range(kill_count):
            kill_ind = result[0]
            for ind in result:
                if ind['score'] < kill_ind['score']:
                    kill_ind = ind
            result.remove(kill_ind)

        #sort (biggest score first) (not neccessary, just for better overview)
        for i in range(len(result)-1):
            for j in range(len(result)-i-1):
                if result[i]['score'] < result[i+1+j]['score']:
                    temp = result[i]
                    result[i] = result[i+1+j]
                    result[i+1+j] = temp

        return result

    def is_valid_genome(self, genome):
        if genome is None:
            return False
        else:
            result = True
            for gene_key, gene_value in genome.items():
                locals()[gene_key] = gene_value

            for constraint in self.constraints:
                result = result and eval(constraint)

            return result


    def get_offspring(self, ind1, ind2):
        genome = None
        while not self.is_valid_genome(genome):
            genome = {}

            for key in ind1.keys():
                if key != 'mate_chance' and key != 'score':
                    if key in ind2:
                        g1 = np.random.normal(ind1[key], np.clip(ind1[key] * self.mutation, 0, None))
                        g2 = np.random.normal(ind2[key], np.clip(ind2[key] * self.mutation, 0, None))
                        genome[key] = random.choice([g1, g2])
                    else:
                        print('not the same genes', ind1, ind2)

                genome['mate_chance'] = 1.0

        return genome


    def breed(self, individuals):

        new_count = self.individual_count-len(individuals)

        result = []
        for ind in individuals:
            result.append(ind.copy())

        weights = np.ones(len(individuals))
        for i, ind in enumerate(individuals):
            if 'mate_chance' in ind:
                weights[i] = ind['mate_chance']

        weights = weights / np.sum(weights)

        for i in range(new_count):
            parent1 = np.random.choice(individuals, 1, p=weights)[0]
            parent2 = np.random.choice(individuals, 1, p=weights)[0]

            result.append(self.get_offspring(parent1, parent2))

        return result

