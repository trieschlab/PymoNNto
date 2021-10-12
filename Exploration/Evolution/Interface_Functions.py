from PymoNNto.Exploration.StorageManager.StorageManager import *
import sys

evolution_genome = None
default_genome = {}

def set_evolution_genome_from_string(gene_str):
    #print('gene_str', gene_str)
    gene_dict = {}
    partial_str = gene_str.split('#')
    for key_value_str in partial_str:
        kv_partial_str = key_value_str.split('@')
        if len(kv_partial_str) == 2:
            if kv_partial_str[0] != 'score':
                gene_dict[kv_partial_str[0]] = kv_partial_str[1] #keys and values are strings!!! have to be casted to default type by get_gene!

    set_genome(gene_dict)

def set_genome(genome):
    #print('set genome to', genome)
    global evolution_genome
    evolution_genome = genome

    if not 'evo_name' in genome:
        print('warning: no evo_name key in evolution for', genome)

def get_genome():
    if evolution_genome is None:
        load_genome()
    return evolution_genome

def cast_to_default(str_value, default):
    if isinstance(default, float) or isinstance(default, int):
        return float(str_value)
    else:
        return str_value

def get_gene(key, default):
    if evolution_genome is None:
        load_genome()

    default_genome[key] = default
    if evolution_genome is not None and key in evolution_genome:
        return cast_to_default(evolution_genome[key], default)
    else:
        return default

def return_default_genome():
    return #todo:implement

def gene(key, default):
    return get_gene(key, default)

def get_gene_id(gene):
    id = ''
    for key, value in gene.items():
        id += '#'+key+'@'+str(value)
    return id+'#'

def get_gene_file(gene):
    return gene['evo_name']+' gen'+str(gene['gen']) + ' id' + str(gene['id'])

def set_score(score, non_evo_storage_manager=None, _genome=None, info={}):
    global evolution_genome

    if _genome is not None:
        evolution_genome = _genome

    if evolution_genome is not None:
        if 'score' in evolution_genome:#only when setscore is called multiple times on accident...
            evolution_genome.pop('score')
        if 'evo_name' in evolution_genome and 'gen' in evolution_genome and 'id' in evolution_genome:
            sm = StorageManager(main_folder_name=get_gene('evo_name', None), folder_name=get_gene_file(evolution_genome), print_msg=False, add_new_when_exists=False)
            evolution_genome['score'] = score
            sm.save_param_dict(evolution_genome)
            sm.save_param_dict(info)
            print('evolution score set to #'+str(score)+'#')
        else:
            print('cannot save score', str(score), 'to file: "evo_name", "gen" or "id" not in genome')
    else:
        print('score='+str(score)+' (no genome found)')
        if non_evo_storage_manager is not None:
            non_evo_storage_manager.save_param('score', score)
            non_evo_storage_manager.save_param_dict(info)

    # reset and reload when next get_gene is called

    evolution_genome = None


def load_genome():
    for arg in sys.argv:
        if 'genome=' in arg:
            set_evolution_genome_from_string(arg[7:])
