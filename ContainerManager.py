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


def main():
    """Main execution function for the server container manager.

    It checks if settings files (for VPN, email, and container) exist, and if not, prompts the user to create them.
    Continuously monitors the VPN container. If it's running, checks the IP, and sends emails if there's an IP change.
    Sleeps for a specified duration before checking again.
    """
    args = helper()

    # Check for VPN settings file existence, and create if not present
    if not os.path.exists(args.VPNdata):
        VPN = {
            'name': input('Enter the name of the docker: '),
            'server_ovpn': input('Enter the path of the server ovpn file: '),
            'client_ovpn': input('Enter the path of the client ovpn file: '),
            'server_ip': VPNManager.get_public_ip() or '169.254.0.1'
        }
        with open(args.VPNdata, 'w') as outfile:
            json.dump(VPN, outfile)

    # Check for email settings file existence, and create if not present
    if not os.path.exists(args.Emaildata):
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
        with open(args.Emaildata, 'w') as outfile:
            json.dump(Email, outfile)

    # Check for container settings file existence, and create if not present
    if not os.path.exists(args.Containerdata):
        Container = {
            'time': input('Enter the time (in seconds) to sleep between checks: ')
        }
        with open(args.Containerdata, 'w') as outfile:
            json.dump(Container, outfile)

    # Main loop for checking the container status and IP
    while True:
        if is_container_running(VPNManager.get_server_setting(args.VPNdata)['name']):
            is_ip_ok = VPNManager.look_ip(args.VPNdata)
            if not is_ip_ok:
                email_data = Server_communication.get_email_settings(args.Emaildata)
                for e in email_data['server_email_client']:
                    Server_communication.send_email(
                        subject='OpenVPN Luxury Ip Change',
                        body='Hello, This is the OpenVPN server of Luxury'
                             'changing IP. Please update your OpenVPN',
                        to_email=e,
                        server_email=email_data['server_email'],
                        server_password=email_data['server_email_password'],
                        attachment_path=VPNManager.get_server_setting(args.VPNdata)['server_ovpn']
                    )
        with open(args.Containerdata, 'r') as c:
            data = json.load(c)
            time.sleep(int(data['time']))


if __name__ == "__main__":
    main()
