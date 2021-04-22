import random
import numpy as np

class Evolution_Base:

    def __init__(self, death_rate, mutation, individual_count):
        self.death_rate = death_rate
        self.mutation = mutation
        self.individual_count = individual_count
        self.generation=1

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

    def get_offspring(self, ind1, ind2):
        result = {}

        for key in ind1.keys():
            if key in ind2:
                g1 = np.random.normal(ind1[key], np.clip(ind1[key] * self.mutation, 0, None))
                g2 = np.random.normal(ind2[key], np.clip(ind2[key] * self.mutation, 0, None))
                result[key] = random.choice([g1, g2])
            else:
                print('not the same genes', ind1, ind2)

        return result


    def breed(self, individuals):

        new_count = self.individual_count-len(individuals)

        result = []
        for ind in individuals:
            result.append(ind.copy())

        weights = np.ones(len(individuals))
        for i, ind in enumerate(individuals):
            if 'breed_chance' in ind:
                weights[i] = ind['breed_chance']

        weights = weights / np.sum(weights)

        for i in range(new_count):
            parent1 = np.random.choice(individuals, 1, p=weights)[0]
            parent2 = np.random.choice(individuals, 1, p=weights)[0]

            result.append(self.get_offspring(parent1, parent2))

        return result

