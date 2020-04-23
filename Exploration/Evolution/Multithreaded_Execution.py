import sys
sys.path.append('../../')

from Exploration.Evolution.Multithreaded_Evolution import *

if __name__ == '__main__':
    from Testing.Old.GrammarExperiment_New import *
    run_multiple_times(run, -1, test_ind)