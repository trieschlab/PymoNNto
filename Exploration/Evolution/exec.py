import sys
import os
#import Exploration.StorageManager.StorageManager as sm
sys.path.append('../../')

name = sys.argv[1]
individual = sys.argv[2]
import_file = sys.argv[3]
func_name = sys.argv[4]

individual=eval(individual)
exec('from ' + import_file + ' import *')
evaluation_function = eval(func_name)

params = {'evolution': True}
if len(sys.argv) > 5:
    for arg in sys.argv[5:]:
        if '=' in arg:
            key, value = arg.split('=')
            params[key] = eval(value)
        else:
            print('no = in argument! (ignored)')
else:
    params['N_e'] = 900
    params['TS'] = [1]

score=evaluation_function(name, individual, params)

#sm.get_data_folder()+

folder = "../../Data/Evo"

if not os.path.exists(folder):
    try:
        os.mkdir(folder)
    except:
        print("main folder already exists")

text_file = open(folder+'/'+name+".txt", "w")
n = text_file.write("score: "+str(score))
text_file.close()
