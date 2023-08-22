import json
import subprocess
import re
import requests
import logging
import argparse
import docker
import time


def get_public_ip():
    try:
        answer = requests.get('https://httpbin.org/ip')
        return answer
    except:
        logging.error("Failed to retrieve public IP")
        return None


def get_server_setting(path: str) -> dict:
    try:
        with open(path, 'r') as setting:
            return json.load(setting)
    except:
        logging.error('Failed to open server settings. Initialising the settings')
        init_setting: dict = {
            'server_public_ip': get_public_ip() if get_public_ip() else '169.254.0.1',
            'server_local_ip': '10.0.0.1',
            'vpn_container_name': 'OpenVPN_server',
            'server_time_to_look': 3600,
            'server_ovpn': 'path/to/file'
        }
        with open(path, 'w') as setting:
            json.dump(init_setting, setting)
        return init_setting


def set_server_setting(value_to_change: str, value: any, path:str) -> None:
    try:
        with open(path, 'rw') as file:
            data = json.load(file)
            data[value_to_change] = value
    except Exception:
        logging.error("Failed to change server data")


def create_vpn_container(container_emplacement: str, port: str, user_name: str, user_password: str,
                         server_local_ip: str, server_name: str):
    client = docker.from_env()

    # Pull the required image
    client.images.pull('kylemanna/openvpn')

    # Volume mapping
    volume_mapping = {container_emplacement: {'bind': '/etc/openvpn', 'mode': 'rw'}}

    # Port mapping
    ports = {f'{port}/udp': port}

    # Create the container
    container = client.containers.create(
        image='kylemanna/openvpn',
        name=server_name,
        volumes=volume_mapping,
        ports=ports,
        cap_add=["NET_ADMIN"],
        restart_policy={"Name": "always"}
    )

    # Start the container
    container.start()

    print(f'{server_name} created and started.')


# Generating a new certificate with a password
def generate_certificate(client_name):
    cmd = [
        "docker", "run",
        "-v", "~/openvpn-data:/etc/openvpn",
        "--rm", "-it",
        "kylemanna/openvpn",
        "easyrsa", "build-client-full",
        client_name, "nopass"
    ]
    subprocess.run(cmd)


# Retrieving the certificate
def get_certificate(client_name):
    cmd = [
        "docker", "run",
        "-v", "~/openvpn-data:/etc/openvpn",
        "--rm",
        "kylemanna/openvpn",
        "ovpn_getclient",
        client_name
    ]
    with open(f"{client_name}.ovpn", "w") as f:
        subprocess.run(cmd, stdout=f)


def update_ovpn_file(filename, new_ip):
    """Replace the IP address in the .ovpn file with the new IP."""
    with open(filename, 'r') as file:
        data = file.read()

    # Match the IP in the "remote" line followed by a port (e.g., 1194)
    data = re.sub(r'(?<=remote\s)(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)\s1194', f'{new_ip} 1194', data)

    with open(filename, 'w') as file:
        file.write(data)

def helper():
    parser = argparse.ArgumentParser(description='I am a homemade Server Container Manager')
    parser.add_argument('-d', '-data', type=str, help='The path to the json containing the data in a json format')
    parser.add_argument('-c', '-create', type=str, help='Create the data in a json format')
    return parser.parse_args()


def main():

    # Set up the helper
    args = helper()

    # Setup logging
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

    if args.data:
        while True:
            current_setting = get_server_setting(args.data)  # look if there was a modification while running
            # Get the VPN container

            current_public_ip = get_public_ip()
            if current_setting['server_public_ip'] != current_public_ip:
                # Need to create new certificate for the new IP address
                update_ovpn_file(current_setting['server_ovpn'], current_public_ip)
                set_server_setting('server_public_ip', current_public_ip, args.data)  # Set the new server settings

            # Get the FPT Container
            time.sleep(current_setting['server_time_to_look'])  # make the script sleep


if __name__ == '__main__':
    main()

