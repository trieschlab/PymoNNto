import sys
sys.path.append('../../')

import subprocess

tag = 'test'
individual = '[0.95, 0.4, 0.1383, 0.1698, 0.1, 0.00015, 0.04, 0.2944, 0.0006, 0.5, 0.015, 0.2944, 0.1, 0.0001, 0.87038, 0.82099, 1.5, 0.08, 15.0]'
import_file='Testing.SORN_Grammar.GrammarExperiment_Hierarchical'
evaluation_function='run'
param = {'N_e': 900, 'TS': [1]}

pexec = 'python exec.py ' + tag + ' ' + individual.replace(' ', '') + ' ' + import_file + ' ' + evaluation_function

for k, v in param.items():
    pexec += ' ' + k + '=' + str(v).replace(' ', '')

print(pexec)
output = subprocess.run(pexec, stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
print(output)

fitness = float(output.split(' ')[-1])

print(fitness)