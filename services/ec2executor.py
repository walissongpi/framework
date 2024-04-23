import boto3
import paramiko
import os
from pathlib import Path

class EC2ApplicationExecutor:
    def __init__(self, logger, ec2, instance_id, instance_data):
        self.logger = logger
        self.ec2 = ec2
        self.instance_id = instance_id
        self.instance_data = instance_data

    def get_instance_ip(self):
        response = self.ec2.describe_instances(InstanceIds=[self.instance_id])
        instance_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
        return instance_ip

    def send_file_to_instance(self, file, folder_destination):

        # Configurações de conexão SSH
        host = self.get_instance_ip()
        username = self.instance_data["user"]
        ssh_key_path = self.instance_data["key_path"]+"/"+self.instance_data["key_name"]+".pem"

        # Caminho do arquivo local que você deseja enviar
        local_file_path = file

        # Caminho de destino na instância remota
        remote_path = folder_destination

        # Criando uma instância SSHClient
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Conectando à instância AWS EC2
        ssh.connect(hostname=host, username=username, key_filename=ssh_key_path)

        # Iniciando o SFTP (Protocolo de Transferência de Arquivos SSH)
        sftp = ssh.open_sftp()

        # Enviando o arquivo para a instância remota
        sftp.put(local_file_path, os.path.join(remote_path, os.path.basename(local_file_path)))

        # Fechando conexão SFTP e SSH
        sftp.close()
        ssh.close()

        self.logger.info("File "+local_file_path+" sent to "+str(host)+":"+str(remote_path)+" successfully!")

    def run_command_on_instance(self, command, command2=None):
        instance_ip = self.get_instance_ip()

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        private_key = paramiko.RSAKey.from_private_key_file(self.instance_data["key_path"]+"/"+self.instance_data["key_name"]+".pem")

        #print(private_key)
        ssh_client.connect(instance_ip, username=self.instance_data["user"], pkey=private_key)
        # Execute the command on the instance
        if command2 is not None:
            stdin, stdout, stderr = ssh_client.exec_command(command2)

        stdin, stdout, stderr = ssh_client.exec_command(command)

        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')


        # Close the SSH connection
        ssh_client.close()
        print(output)
        print(error)

        return output, error
