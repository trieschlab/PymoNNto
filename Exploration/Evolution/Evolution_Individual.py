
def find_individual(id, ind_list):
    for ind in ind_list:
        if ind.id == id:
            return ind



class Evolution_individual:

    def __init__(self, genome, id=None, score=None, mate_chance=None):
        self.id = id
        self.genome = genome
        self.score = score
        self.mate_chance = mate_chance

    def get_copy(self):
        return Evolution_individual(genome = self.genome.copy(), mate_chance = self.mate_chance)

    def is_valid_genome(self, constraints):
        if self.genome is None:
            return False
        else:
            result = True
            for gene_key, gene_value in self.genome.items():
                locals()[gene_key] = gene_value

            for constraint in constraints:
                result = result and eval(constraint)#todo: try except and error message

            return result

        return False

    def has_genes(self, gene_keys):
        for key in gene_keys:
            if not key in self.genome:
                return False
        return True

    def has_compatible_genes(self, individual):
        if len(individual.genome) != len(self.genome): #different gene length
            return False

        for key in individual.genome: #different genes
            if not key in self.genome:
                return False

        return True

    def __str__(self):
        return str(self.genome)

    def __repr__(self):
        return self.__str__()