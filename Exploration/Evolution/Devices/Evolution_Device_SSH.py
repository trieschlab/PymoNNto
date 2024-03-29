from PymoNNto.Exploration.Evolution.Devices.Evolution_Device_Multi_Thread import *
import sys
from PymoNNto.Exploration.Evolution.SSH_Functions import *

def ssh_thread_worker(slave_file, name, ssh_string, root_folder, conn):
    print('ssh thread started')
    while True:
        time.sleep(np.random.rand())
        if conn.poll():
            genome = conn.recv()
            try:

                genome_str=''
                for gene in genome:
                    genome_str+=' '+ str(gene) + '=' + str(genome[gene])

                ssh = get_ssh_connection(ssh_string)
                cmd = 'cd ' + name + '/' +root_folder+ '; '
                cmd += 'python ' + slave_file + genome_str#' genome=' + get_gene_id(genome)
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
                results = get_response(ssh_stdout, ssh_stderr)
                ssh.close()

                success = False
                for line in results:
                    if 'evolution score set to #' in line:
                        parts = line.split('#')
                        if len(parts) == 3:
                            genome['score'] = float(parts[1])
                            success = True

                if success:
                    sm = StorageManager(main_folder_name=genome['evo_name'], folder_name=get_gene_file(genome), print_msg=False, add_new_when_exists=False)
                    sm.save_param_dict(genome)
                    conn.send([genome, 'success'])
                else:
                    conn.send([genome, 'no score found in ssh thread results'+str(results)])

            except:
                conn.send([genome, 'thread error'])

        conn.send([None, 'idle'])
        time.sleep(1.0)


class Evolution_Device_SSH(Evolution_Device_Multi_Thread):

    def __init__(self, device_string, parent):
        super().__init__(device_string, parent)

        temp=sys.argv[0].replace(get_data_folder().replace('Data', ''), '')
        temp='/'.join(temp.split('/')[:-1])#remove file name
        self.root_folder = temp #evolution_master_path_from_project_folder

    def initialize(self):
        self.parent_conn, child_conn = Pipe()
        self.process = Process(target=ssh_thread_worker, args=(self.parent.slave_file, self.parent.name, self.device_string, self.root_folder, child_conn))

    def initialize_device_group(self):
        transfer_project(self.parent.name, self.device_string)
