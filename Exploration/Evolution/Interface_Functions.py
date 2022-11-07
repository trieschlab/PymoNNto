import sys
import os

__evolution_genome__ = {}
__evo_name__ = None
__evo_id__ = None
__evo_generation__ = None

def get_evo_name():
    if __evo_name__ is None:
        update_evolution_parameters()
    return __evo_name__

def get_evo_id():
    if __evo_id__ is None:
        update_evolution_parameters()
    return __evo_id__

def get_evo_generation():
    if __evo_generation__ is None:
        update_evolution_parameters()
    return __evo_generation__

def get_genome():
    if len(__evolution_genome__)==0:
        update_evolution_parameters()
    return __evolution_genome__


def get_gene(key, default):
    if len(__evolution_genome__)==0:
        update_evolution_parameters()

    if not key in __evolution_genome__:
        __evolution_genome__[key] = default

    return cast_to_default(__evolution_genome__[key], default)


def cast_to_default(str_value, default):
    if isinstance(default, float) or isinstance(default, int):
        return float(str_value)
    else:
        return str_value

def gene(key, default):
    return get_gene(key, default)

def set_genome(genome):
    global __evolution_genome__
    __evolution_genome__ = genome

def execute_local_file(file, evo_name, evo_id, evo_generation=0, genome={}, static_genome={}):
    cmd = 'python3 '+file

    cmd+=' __evo_name__' + '="' + evo_name+'"'
    cmd+=' __evo_id__' + '=' + str(evo_id)
    cmd+=' __evo_generation__' + '=' + str(evo_generation)

    for key, value in genome.items():
        cmd+=' ' + str(key) + '="' + str(value)+'"'

    for key, value in static_genome.items():
        cmd+=' ' + str(key) + '="' + str(value)+'"'

    print(os.getcwd(), file)

    os.system(cmd)#python3 file.py __evo_name__=myname __evo_id__=10001 gene1=5 gene2=a gene3=...

def update_evolution_parameters():# pythonfile.py __evo_name__=myname __evo_id__=10001 gene1=5 gene2=a gene3=...
    global __evo_name__
    global __evo_id__
    global __evo_generation__
    global __evolution_genome__

    for arg in sys.argv[1:]:
        if '=' in arg:
            key_value = arg.split('=')
            if len(key_value)==2:
                key = key_value[0]
                value = key_value[1]
                if key == '__evo_name__':
                    __evo_name__ = value
                elif key == '__evo_id__':
                    __evo_id__ = value
                elif key == '__evo_generation__':
                    __evo_generation__ = value
                else:
                    __evolution_genome__[key] = value


def get_gene_file(evo_name, id=None):
    file = evo_name +' id' + str(id)
    return file

def set_score(score, info={}):
    update_evolution_parameters()

    global __evo_name__
    global __evo_id__
    global __evo_generation__
    global __evolution_genome__

    if __evo_name__ is not None and __evo_id__ is not None:
        import PymoNNto.Exploration.StorageManager.StorageManager as storage_manager
        sm = storage_manager.StorageManager(main_folder_name=__evo_name__, folder_name=get_gene_file(__evo_name__, __evo_id__), print_msg=False, add_new_when_exists=False)
        sm.save_param('score', score)
        sm.save_param('evo_name', __evo_name__)
        sm.save_param('id', __evo_id__)
        if __evo_generation__ is not None:
            sm.save_param('generation', __evo_generation__)
            sm.save_param_dict(__evolution_genome__)
        sm.save_param_dict(info)

    __evo_name__ = None
    __evo_id__ = None
    __evo_generation__ = None
    __evolution_genome__ = {}

'''
def set_score(score, non_evo_storage_manager=None, _genome=None, info={}):
    global evolution_genome

    if _genome is not None:
        evolution_genome = _genome

    if 'evo_name' in evolution_genome:#evolution_genome is not None
        if 'score' in evolution_genome:#only when setscore is called multiple times on accident...
            evolution_genome.pop('score')
        #if 'evo_name' in evolution_genome:# and 'generation' in evolution_genome and 'id' in evolution_genome
        sm = StorageManager(main_folder_name=get_gene('evo_name', None), folder_name=get_gene_file(evolution_genome), print_msg=False, add_new_when_exists=False)
        evolution_genome['score'] = score
        sm.save_param_dict(evolution_genome)
        sm.save_param_dict(info)
        print('evolution score set to #'+str(score)+'#')
        #else:
        #    print('cannot save score', str(score), 'to file: "evo_name", "gen" or "id" not in genome')
    else:
        print('score='+str(score)+' (no genome found)')
        if non_evo_storage_manager is not None:
            non_evo_storage_manager.save_param('score', score)
            non_evo_storage_manager.save_param_dict(info)

    # reset and reload when next get_gene is called

    evolution_genome = None
'''



###############################old

#def get_default_genome():
#    return default_genome

#def get_gene_file(gene):
#    file = gene['evo_name']
#    if 'generation' in  gene:
#        file+=' gen' + str(gene['generation'])
#    if 'id' in gene:
#        file += ' id' + str(gene['id'])
#    return file

#def load_genome2():
#    for arg in sys.argv:
#        if 'genome=' in arg:
#            set_evolution_genome_from_string(arg[7:])

#def set_evolution_genome_from_string(gene_str):
#    #print('gene_str', gene_str)
#    gene_dict = {}
#    partial_str = gene_str.split('#')
#    for key_value_str in partial_str:
#        kv_partial_str = key_value_str.split('@')
#        if len(kv_partial_str) == 2:
#            if kv_partial_str[0] != 'score':
#                gene_dict[kv_partial_str[0]] = kv_partial_str[1] #keys and values are strings!!! have to be casted to default type by get_gene!
#
#    set_genome(gene_dict)

#######################################

#def get_gene_id(gene):
#    id = ''
#    for key, value in gene.items():
#        id += '#'+key+'@'+str(value)
#    return id+'#'


#def execute_local_file(file, evo_name, evo_id, evo_generation, genome, static_genome={}): #file.py __evo_name__=myname __evo_id__=10001 gene1=5 gene2=a gene3=...
#    py_file = open(file, "r")
#    file_content = py_file.read()
#    py_file.close()

    #remove old infomation
#    for arg in sys.argv:
#        if '=' in arg:
#            sys.argv.remove(arg)

#    global __evo_name__
#    global __evo_id__
#    global __evo_generation__
#    global __evolution_genome__
#    __evo_name__ = None
#    __evo_id__ = None
#    __evo_generation__ = None
#    __evolution_genome__= {}

    #add new information
#    sys.argv.append('__evo_name__' + '=' + evo_name)
#    sys.argv.append('__evo_id__' + '=' + str(evo_id))
#    sys.argv.append('__evo_generation__' + '=' + str(evo_generation))

#    for key, value in genome.items():
#        sys.argv.append(str(key) + '=' + str(value))

#    for key, value in static_genome.items():
#        sys.argv.append(str(key) + '=' + str(value))

#    exec(file_content)