import json
import logging
import os
import time
import docker
import VPNManager
import Server_communication

# Setting up the logging configuration
logging.basicConfig(level=logging.INFO)


def helper():
    """Sets up the argument parser and defines command-line arguments.

    Returns:
        args: Parsed command-line arguments.
    """
    import argparse
    parser = argparse.ArgumentParser(description='I am a homemade Server Container Manager')
    parser.add_argument('-vd', '--VPNdata', type=str, required=True, help='Path to the VPN settings')
    parser.add_argument('-ed', '--Emaildata', type=str, required=True, help='Path to the email settings')
    parser.add_argument('-cd', '--Containerdata', type=str, required=True, help='Path to the Container settings')
    parser.add_argument('-t', '--time', type=int, required=True, help='Time for check up in second')
    return parser.parse_args()


def is_container_running(container_name_or_id):
    """Checks if a given Docker container (by name or ID) is currently running.

    Args:
        container_name_or_id (str): Name or ID of the Docker container.

    Returns:
        bool: True if the container is running, False otherwise.
    """
    try:
        client = docker.from_env()
        container = client.containers.get(container_name_or_id)
        return container.status == "running"
    except Exception as e:
        logging.error(f"Failed to get container status for {container_name_or_id}. Error: {e}")
        return False


def server_wait(container_data_path: str):
    with open(container_data_path, 'r') as c:
        data = json.load(c)
        time.sleep(int(data['time']))


def data_verification(path_to_data: str, type_of_data: str):
    try:
        with open(path_to_data, 'r') as file:
            if not json.load(file):
                logging.error(f'{type_of_data} FILE NOT FOUND STOPING PROGRAM')
                exit()
    except:
        logging.error(f'COULD NOT OPEN {type_of_data} DATA. CLOSING PROGRAM')
        exit()


def server_comunication(path_to_email_data: str, path_to_vpn_data: str):
    email_data = Server_communication.get_email_settings(path_to_email_data)
    for e in email_data['server_email_client']:
        Server_communication.send_email(
            subject='OpenVPN Luxury Ip Change',
            body='Hello, This is the OpenVPN server of Luxury'
                 'changing IP. Please update your OpenVPN',
            to_email=e,
            server_email=email_data['server_email'],
            server_password=email_data['server_email_password'],
            attachment_path=VPNManager.get_server_setting(path_to_vpn_data)['server_ovpn']
        )


def vpn_data_creation_process(path_to_file: str):
    VPN = {
        'name': input('Enter the name of the docker: '),
        'server_ovpn': input('Enter the path of the server ovpn file: '),
        'client_ovpn': input('Enter the path of the client ovpn file: '),
        'server_ip': VPNManager.get_public_ip() or '169.254.0.1'
    }
    with open(path_to_file, 'w') as outfile:
        json.dump(VPN, outfile)


def server_email_creation_proces(path_to_file: str):
    client = []
    while True:
        user_input = input('Enter an email (or -q to quit): ')
        if user_input.lower() == '-q':
            break
        client.append(user_input)
    Email = {
        'server_email': input('Enter the server email: '),
        'server_email_password': input('Enter the password of the server email: '),
        'server_email_client': client
    }
    with open(path_to_file, 'w') as outfile:
        json.dump(Email, outfile)


def server_container_data_creation_process(path_to_file: str):
    container = {
        'time': input('Enter the time (in seconds) to sleep between checks: ')
    }
    with open(path_to_file, 'w') as outfile:
        json.dump(container, outfile)


def main():
    """Main execution function for the server container manager.

    It checks if settings files (for VPN, email, and container) exist, and if not, prompts the user to create them.
    Continuously monitors the VPN container. If it's running, checks the IP, and sends emails if there's an IP change.
    Sleeps for a specified duration before checking again.
    """
    args = helper()

    # Check for VPN settings file existence, and create if not present
    if not os.path.exists(args.VPNdata):
        vpn_data_creation_process(args.VPNdata)

    # Check for email settings file existence, and create if not present
    if not os.path.exists(args.Emaildata):
        server_email_creation_proces(args.Emaildata)

    # Check for container settings file existence, and create if not present
    if not os.path.exists(args.Containerdata):
        server_container_data_creation_process(args.Containerdata)

    # Main loop for checking the container status and IP
    while True:  # running process

        if not is_container_running(VPNManager.get_server_setting(args.VPNdata)['name']):
            time.sleep(300)

        is_ip_ok = VPNManager.look_ip(args.VPNdata)

        if is_ip_ok is None:
            data_verification(args.VPNdata, 'VPN')
            time.sleep(180)
            pass

        if is_ip_ok:
            server_wait(args.Containerdata)
            pass

        server_comunication(args.Containerdata, args.VPNdata)

        server_wait(args.Containerdata)


if __name__ == "__main__":
    main()
