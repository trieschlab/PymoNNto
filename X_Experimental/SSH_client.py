import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('hey3kmuagjunsk2b.myfritz.net', username='marius')
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('ls -la')

#print(ssh_stdin.read())
print(ssh_stdout.read().decode('utf-8'))
#print(ssh_stderr.read())
ssh.close()