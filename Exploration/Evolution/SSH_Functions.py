from PymoNNto.Exploration.StorageManager.StorageManager import *
import paramiko
from scp import SCPClient

def is_invalid_evo_name(name):
    return '/' in name or '.' in name or ' ' in name or '   ' in name or '\\' in name or name in ['Documents', 'Pictures', 'Music', 'Public', 'Videos', 'Dokumente', 'Bilder', 'Musik', 'Downloads', 'Öffentlich']


def get_ssh_connection(host, user, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    return ssh

def get_response(out, err):
    result = []
    for line in out.read().splitlines():
        result.append(line.decode("utf-8"))
    for line in err.read().splitlines():
        result.append(line.decode("utf-8"))
    return result

def split_ssh_user_host_password_string(user_host_pw_str):
    password = None
    user = None
    host = None
    user_host = user_host_pw_str.replace('ssh ', '').split('@')
    if len(user_host) == 2:
        user = user_host[0]
        host = user_host[1]
        if ' ' in host:
            host_pw = host.split(' ')
            if len(host_pw) == 2:
                host = host_pw[0]
                password = host_pw[1]
                print('warning: a clear text ssh password inside of the code is dangerous!')
            else:
                print('space in host but no password detected')
    else:
        print('cannot split user and host')

    return user, host, password

def zip_project(Main_Folder, zip_file_path):
    zipDir(Main_Folder, zip_file_path, ['.git', '.zip', '.idea', '\\Evolution_Project_Clones\\', '\\StorageManager\\', '\\NetworkStates\\', '\\Evo\\', '\\__pycache__\\', '\\midis\\'])

def get_epc_folder(create=True):
    Data_Folder = get_data_folder()
    if Data_Folder != './Data':
        epc_folder = Data_Folder + '/Evolution_Project_Clones'
        create_folder_if_not_exist(epc_folder)
        return epc_folder
    return None

def clone_project(name):
    epc_folder = get_epc_folder()
    if epc_folder is not None:
        Main_Folder = epc_folder.replace('Data/Evolution_Project_Clones', '')

        src = epc_folder + '/' + name + '.zip'
        zip_project(Main_Folder, src)

        zipf = zipfile.ZipFile(src, mode='r')
        zipf.extractall(path=epc_folder + '/' + name, members=None, pwd=None)
        zipf.close()

        os.remove(src)
        return epc_folder+'/'+name+'/'
    else:
        print('Error No root "Data" folder found')

def transfer_project(name, user, host, password=None):
    # search main project folder
    Data_Folder = get_data_folder()
    if Data_Folder != './Data':
        Main_Folder = Data_Folder.replace('Data', '')

        src = Data_Folder + '/' + name + '.zip'
        dst = name + '.zip'

        # zip project
        print('Create Zip File from current folder:')
        zip_project(Main_Folder, src)

        # transfer
        print('Transfer zip to', host)
        ssh = get_ssh_connection(host, user, password)
        scp = SCPClient(ssh.get_transport())
        scp.put(src, dst)

        # remove zip
        os.remove(src)

        # remote unzip and remote remove zip
        print('Extract zip at', host)
        cmd = 'rm -r -d ' + name + '; '  # remove old directory
        cmd += 'mkdir ' + name + '; '  # create new directory
        cmd += 'unzip ' + name + '.zip -d ' + name + '; '  # unzip
        cmd += 'rm ' + name + '.zip'  # remove zip
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
        print(get_response(ssh_stdout, ssh_stderr))

        scp.close()
        ssh.close()
    else:
        print('Error No root "Data" folder found')

def get_Data(name, user, host, password):
    # search main project folder
    Data_Folder = get_data_folder()
    if Data_Folder != './Data':

        src = name + '/Data.zip'
        dst_path = get_epc_folder()+'/'+name+'/' #test.zip
        dst = dst_path + 'Data.zip'

        print(src,dst_path,dst)

        ssh = get_ssh_connection(host, user, password)

        # zip project
        cmd = 'cd ' + name + ' ; '
        cmd += 'zip -r Data.zip Data ;'
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
        print(get_response(ssh_stdout, ssh_stderr))

        # transfer
        print('Transfer zip from', host)
        scp = SCPClient(ssh.get_transport())
        scp.get(src, dst)

        with zipfile.ZipFile(dst, "r") as zip_ref:
            zip_ref.extractall(dst_path)

        # remove zip
        cmd = 'cd ' + name + '; '
        cmd += 'rm Data.zip; '
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
        print(get_response(ssh_stdout, ssh_stderr))
        os.remove(dst)

        scp.close()
        ssh.close()
    else:
        print('Error No root "Data" folder found')

def ssh_execute_evo(server, name, python_cmd='python3'):
    user, host, password = split_ssh_user_host_password_string(server)
    ssh = get_ssh_connection(host, user, password)

    command = 'cd ' + name + '; '
    #command = 'nano .bashrc'
    command += 'screen -dmS ' + name + ' sh; screen -S ' + name + ' -X stuff "'+python_cmd+' execute_evolution.py \r\n"'

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
    response = get_response(ssh_stdout, ssh_stderr)
    print(response)

    ssh.close()

def ssh_stop_evo(server, name, remove_evo=False):
    user, host, password = split_ssh_user_host_password_string(server)
    ssh = get_ssh_connection(host, user, password)

    command = 'screen -XS ' + name + ' quit;'
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
    response = get_response(ssh_stdout, ssh_stderr)
    print(response)

    if remove_evo:
        command = 'rm -r ' + name
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
        response = get_response(ssh_stdout, ssh_stderr)
        print(response)

    ssh.close()

def ssh_get_running(server):
    response=''
    try:
        user, host, password = split_ssh_user_host_password_string(server)
        ssh = get_ssh_connection(host, user, password)

        command = 'screen -ls'
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command, timeout=10)
        response = get_response(ssh_stdout, ssh_stderr)
        print(response)

        ssh.close()
    except:
        print(server, 'no response')

    result = []

    for l in response:
        if '	' in l:
            dot_split = l.split('.')
            if len(dot_split) > 1:
                space_split = dot_split[1].split('	')
                if len(space_split) > 0:
                    result.append(space_split[0])

    return result


