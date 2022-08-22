import paramiko

class RouterOSSession():
    def __init__(self, ip="192.168.1.1", port="22", username=None, password=None, timeout=20, ssh_key_file=None,
                 ssh_key_passphrase=None, use_keys=True, pkey=None):
        self.ssh = paramiko.SSHClient()
        self.transport = self.ssh.get_transport()
        self.sftp = None

        # SSH keys
        # TODO: Insecure, risk of MITM attacks:
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.pkey = paramiko.RSAKey.from_private_key_file(filename=ssh_key_file, password=ssh_key_passphrase)

        # Router connection info
        self.ip = ip
        self.port = port
        self.passphrase = ssh_key_passphrase
        self.username = username
        self.password = password

        # Connection settings
        self.timeout = timeout

    def send_ssh_command(self, command: str):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        # Wait for command to finish before continuing with script:
        stdout.channel.set_combine_stderr(True)
        output = stdout.readlines()
        return output

    def send_ssh_command_list(self, command_list: str):
        output_list = []
        for command in command_list:
            output_list.append(self.send_ssh_command(command))
        return output_list

    def ssh_connect(self):
        self.ssh.connect(self.ip, int(self.port), self.username, self.password, self.pkey, passphrase=self.passphrase,
                         timeout=self.timeout,
                         disabled_algorithms={'keys': ['rsa-sha2-512'], 'pubkeys': ["rsa-sha2-512"]})

    def sftp_connect(self):
        #if self.transport.is_active():
        self.sftp = self.ssh.open_sftp()

    def sftp_get_file(self, remote_file, download_filepath):
        self.sftp.get(remote_file, download_filepath)

    def sftp_delete_file(self, remote_file):
        self.sftp.remove(remote_file)

    def disconnect(self):
        try:
            self.sftp.close()
            self.ssh.close()
        except:
            pass

    def backup(self, backup_filename, encrypt_password=None):
        if encrypt_password:
            self.send_ssh_command("/system backup save name={0} password={1}".format(backup_filename, encrypt_password))
        else:
            self.send_ssh_command("/system backup save name={0}".format(backup_filename))
        return backup_filename
