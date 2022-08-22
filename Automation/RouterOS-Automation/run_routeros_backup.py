import yaml
import datetime
import logging
import paramiko
from linux_utilities import delete_files_older_than
import routeros_session

l = logging.getLogger("paramiko")
l.setLevel(paramiko.common.DEBUG)
paramiko.util.log_to_file('microtik-backup-script.log')


def session_from_yml(router_config, global_config):
    key_fullpath = global_config['ssh_key_file']
    ip = router_config['ip']
    port = router_config['port']
    username = router_config['username']
    password = router_config['password']
    timeout = router_config['timeout']
    passphrase = router_config['passphrase']
    session = routeros_session.RouterOSSession(ip, port, username, password, timeout, key_fullpath, passphrase)
    return session


def load_router_yml(yaml_file):
    with open(yaml_file, 'r') as config_file:
        return yaml.safe_load(config_file)


config = load_router_yml('routeros_credentials.yml')
# Get a list of router names, don't append 'global_config' entry
router_names = [item for item in config if item != 'global_config']

# Get the global config
global_config = config['global_config']

# Download path (for backup files)
download_path = global_config['sftp_download_path']

# Backup each router
for router_name in router_names:
    # Get configuration for individual router in this iteration:
    router_config = config[router_name]
    # We have to pass global_config for SSH key information
    router_session = session_from_yml(router_config, global_config)

    # Connect to SSH
    router_session.ssh_connect()

    # Get a formatted date time string
    date = datetime.datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
    # Filename has datetime of backup
    backup_filename = router_config['ip'] + f"_{date}.backup"

    # Create a backup of the current router config
    router_session.backup(backup_filename)

    router_session.sftp_connect()
    # Download and delete file
    router_session.sftp_get_file(backup_filename, download_path + backup_filename)
    # Delete backup file off router after it is downloaded, to free up space)
    router_session.sftp_delete_file(backup_filename)

    # Disconnect from ssh/sftp
    router_session.disconnect()

# Delete router backups older than 30 days:
delete_files_older_than(download_path, 30)

print("Router backup script has completed.")
