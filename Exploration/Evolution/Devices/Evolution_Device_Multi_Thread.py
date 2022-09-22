from PymoNNto.Exploration.Evolution.Devices.Evolution_Device import *
from multiprocessing import Process, Pipe
#import subprocess
#import time
#import os
import numpy as np
import sys
import traceback

def local_thread_worker(slave_file, evo_name, static_genome, conn):
    #try:
    #    import psutil as psu
    #    parent = psu.Process()
    #    parent.nice(psu.BELOW_NORMAL_PRIORITY_CLASS)
    #except:
    #    print('not able to set BELOW_NORMAL_PRIORITY_CLASS')
    print('local thread started')
    while True:
        time.sleep(np.random.rand()/10)#avoid creating same storage manager files at same time
        if conn.poll():
            evo_id, generation, genome = conn.recv()
            try:
                execute_local_file(slave_file, evo_name, evo_id, generation, genome, static_genome)
                conn.send([evo_id, 'success'])
            except Exception as e:
                error_type = str(sys.exc_info()[0])
                msg = str(sys.exc_info()[1])
                conn.send([genome, 'thread error '+error_type+' '+msg+'\r\n'+traceback.format_exc()])

        conn.send([None, 'idle'])


class Evolution_Device_Multi_Thread(Evolution_Device):

    def initialize(self):
        self.parent_conn, child_conn = Pipe()
        self.process = Process(target=local_thread_worker, args=(self.parent.slave_file, self.parent.name, self.parent.inactive_genome_info, child_conn))

    def main_loop_update(self):

        if self.parent_conn.poll():
            evo_id, thread_msg = self.parent_conn.recv()
            if thread_msg == 'success':
                self.score_processing(evo_id)
            elif thread_msg == 'idle':
                current_individual = self.parent.get_next_individual()
                if current_individual is not None:
                    arguments = [current_individual.id, self.parent.Breed_And_Select.generation, current_individual.genome]
                    self.parent_conn.send(arguments)
            else:
                self.parent.error_event(evo_id, thread_msg)

    def start(self):
        self.process.start()

    def stop(self):
        self.process.stop()#???


