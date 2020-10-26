import subprocess
import os
from multiprocessing import Process, Queue, Pipe

def exec(i):
    while True:
        cmd = ['ssh', 'marius@hey3kmuagjunsk2b.myfritz.net', '-t', 'cd Evolution/evx/Exploration/Evolution/; python3 exec.py evy [1.0028996908687935,0.38690475981388583,0.1415680013604927,0.15851683745698486,0.09308438886555265,0.00015873849934684248,0.042893453476295536,0.30467115007125734,0.0006697315588190449,0.5265039176742216,0.014124932025635528,0.29437390007215253,0.09916394643686156,0.00010784505251459317,0.9325069492667815,0.828990043433448,1.6091662763246406,0.07928817306514384,15.145360057684574] Testing.SORN_Grammar.GrammarExperiment_Hierarchical run evolution=True N_e=900 TS=[1]']

        output = subprocess.run(cmd, stdout=subprocess.PIPE)
        print(output)
        fitness = output.split(' ')[-1].replace('\r', '').replace('\n', '')
        if fitness.replace('.', '').isnumeric():
            fitness = float(fitness)
        else:
            fitness = None
        print(i, fitness)

if __name__ == '__main__':
    for i in range(1):
        p = Process(target=exec, args=(i,))
        p.start()
