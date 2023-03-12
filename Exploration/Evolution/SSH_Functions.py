from PymoNNto.Exploration.StorageManager.StorageManager import *
import paramiko
from scp import SCPClient

def is_invalid_evo_name(name):
    return '/' in name or '.' in name or ' ' in name or '   ' in name or '\\' in name or name in ['Documents', 'Pictures', 'Music', 'Public', 'Videos', 'Dokumente', 'Bilder', 'Musik', 'Downloads', 'Öffentlich']


def get_ssh_connection(ssh_string):#host, user, password
    host, user, password, port = split_ssh_user_host_password_string(ssh_string)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port=port, username=user, password=password)
    return ssh

def get_response(out, err):
    result = []
    for line in out.read().splitlines():
        result.append(line.decode("utf-8"))
    for line in err.read().splitlines():
        result.append(line.decode("utf-8"))
    return result

def split_ssh_user_host_password_string(ssh_string, messages=True):
    password = None
    user = None
    host = None
    port = 22
    is_ssh = False

    parts = ssh_string.split(' ')

    try:

        for i in range(len(parts)):

            if i==0 and parts[i]=='ssh':
                is_ssh=True

            if '@' in parts[i]:
                user, host = parts[i].split('@')

            if parts[i]=='-p' or parts[i]=='port':
                port = int(parts[i+1])

            if parts[i]=='password':
                password = parts[i+1]

    except:
        is_ssh = False

    if is_ssh:
        return host, user, password, port
    else:
        return None, None, None, None


    #user_host = user_host_pw_str.replace('ssh ', '').split('@')
    #if len(user_host) == 2:
    #    user = user_host[0]
    #    host = user_host[1]
    #    if ' ' in host:
    #        host_pw = host.split(' ')
    #        if len(host_pw) == 2:
    #            host = host_pw[0]
    #            password = host_pw[1]
    #            if messages:
    #                print('warning: a clear text ssh password inside of the code is dangerous!')
    #        else:
    #            if messages:
    #                print('space in host but no password detected')
    #else:
    #    if messages:
    #        print('cannot split user and host')
    #return user, host, password

def zip_project(Main_Folder, zip_file_path):
    zipDir(Main_Folder, zip_file_path, ['.git', '.zip', '.idea', '\\Evolution_Project_Clones\\', '\\Plot_Project_Clones\\', '\\Execution_Project_Clones\\', '\\StorageManager\\', '\\NetworkStates\\', '\\Evo\\', '\\__pycache__\\', '\\midis\\'])

def get_epc_folder(main_folder='Evolution_Project_Clones', create=True):
    Data_Folder = get_data_folder()
    if Data_Folder != './Data':
        epc_folder = Data_Folder + '/'+main_folder
        create_folder_if_not_exist(epc_folder)
        return epc_folder
    return None

def clone_project(name, folder):
    epc_folder = get_epc_folder(folder)
    if epc_folder is not None:
        Main_Folder = epc_folder.replace('Data/'+folder, '')

        src = epc_folder + '/' + name + '.zip'
        zip_project(Main_Folder, src)

        zipf = zipfile.ZipFile(src, mode='r')
        zipf.extractall(path=epc_folder + '/' + name, members=None, pwd=None)
        zipf.close()

        os.remove(src)
        return epc_folder+'/'+name+'/'
    else:
        print('Error No root "Data" folder found')

def transfer_project(name, device_string):
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
        print('Transfer zip to', device_string)
        ssh = get_ssh_connection(device_string)
        scp = SCPClient(ssh.get_transport())
        scp.put(src, dst)

        # remove zip
        os.remove(src)

        # remote unzip and remote remove zip
        print('Extract zip at', device_string)
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

def transfer_project_back(name, device_string, main_folder='Evolution_Project_Clones'):
    # search main project folder
    Data_Folder = get_data_folder()
    if Data_Folder != './Data':

        src = '_transfer.zip'
        dst_path = get_epc_folder(main_folder)+'/'#+name+'/' #test.zip
        dst = dst_path + '_transfer.zip'

        print(src,dst_path,dst)

        ssh = get_ssh_connection(device_string)

        # zip project
        #cmd = 'cd ' + name + ' ; '
        cmd = 'zip -r _transfer.zip '+ name +' ;'
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
        print(get_response(ssh_stdout, ssh_stderr))

        # transfer
        print('Transfer zip from', device_string)
        scp = SCPClient(ssh.get_transport())
        scp.get(src, dst)

        with zipfile.ZipFile(dst, "r") as zip_ref:
            zip_ref.extractall(dst_path)

        # remove zip
        cmd = 'rm _transfer.zip; '
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
        print(get_response(ssh_stdout, ssh_stderr))
        os.remove(dst)

        scp.close()
        ssh.close()
    else:
        print('Error No root "Data" folder found')

def get_Data(name, device_string, main_folder='Evolution_Project_Clones'):
    # search main project folder
    Data_Folder = get_data_folder()
    if Data_Folder != './Data':

        src = name + '/Data.zip'
        dst_path = get_epc_folder(main_folder)+'/'+name+'/' #test.zip
        dst = dst_path + 'Data.zip'

        print(src,dst_path,dst)

        ssh = get_ssh_connection(device_string)

        # zip project
        cmd = 'cd ' + name + ' ; '
        cmd += 'zip -r Data.zip Data ;'
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
        print(get_response(ssh_stdout, ssh_stderr))

        # transfer
        print('Transfer zip from', device_string)
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

def ssh_execute_evo(server, name):
    ssh = get_ssh_connection(server)

    command = 'cd ' + name + '; '
    #command = 'nano .bashrc'
    command += 'screen -dmS ' + name + ' sh; screen -S ' + name + ' -X stuff "python3 execute.py \r\n"'

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
    response = get_response(ssh_stdout, ssh_stderr)
    print(response)

    ssh.close()

def ssh_remove_evo(server, name):
    ssh = get_ssh_connection(server)

    command = 'rm -r ' + name
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
    response = get_response(ssh_stdout, ssh_stderr)
    print(response)

    ssh.close()

def ssh_stop_evo(server, name, remove_evo=False):
    ssh = get_ssh_connection(server)

    command = 'screen -XS ' + name + ' quit;'
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
    response = get_response(ssh_stdout, ssh_stderr)
    print(response)

    #if remove_evo:
    #    command = 'rm -r ' + name
    #    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
    #    response = get_response(ssh_stdout, ssh_stderr)
    #    print(response)

    ssh.close()

def ssh_get_running(server):
    response=''
    try:
        ssh = get_ssh_connection(server)

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


