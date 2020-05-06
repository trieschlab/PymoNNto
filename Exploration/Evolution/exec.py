import sys
import os
#import Exploration.StorageManager.StorageManager as sm
sys.path.append('../../')


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

params=args_to_param_dict()


import_file=params.get('import_file', 'Testing.SORN_Grammar.GrammarExperiment_Hierarchical')
exec('from ' + import_file + ' import *')

func_name=params.get('func_name', 'run')
evaluation_function = eval(func_name)

score = evaluation_function(params)

print('score:', score)

#name = sys.argv[1]
#individual = sys.argv[2]
#import_file = sys.argv[3]
#func_name = sys.argv[4]

#individual=eval(individual)
#exec('from ' + import_file + ' import *')
#evaluation_function = eval(func_name)

#params = {'evolution': True}
#if len(sys.argv) > 5:
#    for arg in sys.argv[5:]:
#        if '=' in arg:
#            key, value = arg.split('=')
#            params[key] = eval(value)
#        else:
#            print('no = in argument! (ignored)')
#else:
#    params['N_e'] = 900
#    params['TS'] = [1]

#sm.get_data_folder()+

#folder = "../../Data/Evo"

#if not os.path.exists(folder):
#    try:
#        os.mkdir(folder)
#    except:
#        print("main folder already exists")

#text_file = open(folder+'/'+name+".txt", "w")
#n = text_file.write("score: "+str(score))
#text_file.close()
