from PymoNNto.Exploration.Evolution.Devices.Evolution_Device import *
from multiprocessing import Process, Pipe
#import subprocess
#import time
#import os
import numpy as np
import sys


def local_thread_worker(slave_file, conn):
    #try:
    #    import psutil as psu
    #    parent = psu.Process()
    #    parent.nice(psu.BELOW_NORMAL_PRIORITY_CLASS)
    #except:
    #    print('not able to set BELOW_NORMAL_PRIORITY_CLASS')
    print('local thread started')
    while True:
        time.sleep(np.random.rand()/10)
        if conn.poll():
            genome = conn.recv()
            try:
                execute_local_file(slave_file, genome)
                conn.send([genome, 'success'])
            except Exception as e:
                error_type = str(sys.exc_info()[0])
                msg = str(sys.exc_info()[1])
                conn.send([genome, 'thread error '+error_type+' '+msg])

        conn.send([None, 'idle'])


class Evolution_Device_Multi_Thread(Evolution_Device):

    def get_score(self, genome):
        sm = StorageManager(main_folder_name=genome['evo_name'], folder_name=get_gene_file(genome), add_new_when_exists=False)#, print_msg=False
        return sm.load_param('score', default=None)

    def initialize(self):
        self.parent_conn, child_conn = Pipe()
        self.process = Process(target=local_thread_worker, args=(self.parent.slave_file, child_conn))

    def start(self):
        self.process.start()

    def main_loop_update(self):

        if self.parent_conn.poll():
            genome, thread_msg = self.parent_conn.recv()

            #print(thread_msg)

            if thread_msg == 'success':
                self.score_processing(genome)

            elif thread_msg == 'idle':
                current_genome = self.parent.get_next_genome()
                if current_genome is not None:
                    self.parent_conn.send(current_genome)
                #else:
                #    print('no genes found to process')

            else:
                self.error_event(genome, thread_msg)


    def stop(self):
        return
        #self.process.stop()#???


