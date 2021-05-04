from PymoNNto.Exploration.Evolution.Evolution import *

if __name__ == '__main__':
    genome = {'a': 1, 'b': 2, 'c': 2, 'd': 2, 'e':3}

    evo = Evolution(name='my_test_evo',
                    slave_file='test_slave.py', #Exploration/Evolution/
                    individual_count=10,
                    mutation=0.04,
                    death_rate=0.5,
                    constraints=['b>=a', 'a<=1', 'b>= 2'],
                    inactive_genome_info={'info': 'my_info'},
                    start_genomes=[genome],
                    devices={'single_thread': 0,
                             'multi_thread': 4,
                             'ssh vieth@poppy.fias.uni-frankfurt.de': 0,
                             'ssh marius@hey3kmuagjunsk2b.myfritz.net': 0,
                             }
                    )

    if not evo.start(ui=True):
        evo.continue_evolution(ui=True)
