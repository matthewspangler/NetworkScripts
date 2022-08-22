"""
In order for this script to work, you must have generated SSH keys, and uploaded your private key to the router.
Specify the path to the SSH public key by editing the ssh_keyfile variable.
"""

import datetime
import logging
import paramiko
from Libraries.linux_utilities import delete_files_older_than

# TODO: - save credentials more securely!
home = "/home/matt"
download_path = "{}/Net-Admin-Stuff/Router-Backups/".format(home)
ssh_key_file = "{}/.ssh/id_rsa".format(home)
ssh_config_file = "{}/.ssh/config".format(home)
ssh_port = 10022
ssh_key_passphrase = ''
routeros_user = 'admin'
routeros_password = ''
use_keys = True

ssh = paramiko.SSHClient()
transport = ssh.get_transport()
# TODO: Insecure, risk of MITM attacks:
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_key = paramiko.RSAKey.from_private_key_file(filename=ssh_key_file, password=ssh_key_passphrase)

router_list = {
    '10.10.0.2':
        {
            'port': ssh_port,
            'passphrase': ssh_key_passphrase,
            'username': routeros_user,
            'password': routeros_password,
            'pkey': ssh_key,
            'timeout': 20,
            'disabled_algorithms': {'keys': ['rsa-sha2-512'], 'pubkeys': ["rsa-sha2-512"]}
        },
    '10.10.0.4':
        {
            'port': ssh_port,
            'passphrase': ssh_key_passphrase,
            'username': routeros_user,
            'password': routeros_password,
            'pkey': ssh_key,
            'timeout': 20,
            'disabled_algorithms': {'keys': ['rsa-sha2-512'], 'pubkeys': ["rsa-sha2-512"]}
        }
}

l = logging.getLogger("paramiko")
l.setLevel(paramiko.common.DEBUG)
paramiko.util.log_to_file('microtik-backup-script.log')


def send_ssh_command(ssh_client: paramiko.SSHClient, command: str):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    # Wait for command to finish before continuing with script:
    stdout.channel.set_combine_stderr(True)
    output = stdout.readlines()
    return output


def backup_router(hostname: str, params: dict):
    # TODO: delete router backups older than a certain date
    # TODO: setup a chron job for this script
    ssh.connect(hostname, **params)

    # Get a formatted date time string
    date = datetime.datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
    backup_filename = hostname + f"_{date}.backup"

    command_list = [
        "/system backup save name={0} password=1MelroseFarm1".format(backup_filename),
        "/file print"
    ]

    for command in command_list:
        send_ssh_command(ssh, command)

    # Download backup file via SFTP
    sftp = ssh.open_sftp()
    sftp.get(backup_filename, download_path + backup_filename)
    # Delete backup file off router after it is downloaded, to free up space
    sftp.remove(backup_filename)
    # send_ssh_command(ssh, '/file remove "{}""'.format(backup_filename))

    sftp.close()
    ssh.close()


for hostname, params in router_list.items():
    backup_router(hostname, params)

# Delete router backups older than 30 days:
delete_files_older_than(download_path, 30)

print("Router backup script has completed.")
