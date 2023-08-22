import json

import docker
import logging
import argparse

import VPNManager
import Server_communication
def helper():
    parser = argparse.ArgumentParser(description='I am a homemade Server Container Manager')
    parser.add_argument('-vd', '-VPNdata', type=str, help='Path to the VPN settings')
    parser.add_argument('-ed', '-Emaildata', type=str, help='Path to the email settings')
    parser.add_argument('-cd', '-Containerdata', type=str, help='Path to the Container settings')
    parser.add_argument('-c', '-create', type=str, help='Create the data in a json format')
    parser.add_argument('-t','time',type=int, help='Time for check up in second')
    return parser.parse_args()


def is_container_running(container_name_or_id: str) -> bool:
    client = docker.from_env()
    try:
        container = client.containers.get(container_name_or_id)
        return container.status == 'running'
    except:
        logging.error('Error in the container research')
        return False


def main():
    args = helper()
    if args.VPNdata:
        with open(args.VPNdata, 'r') as v:
            VPN_data = json.load(v)
            if is_container_running(VPN_data['name']):
                is_ip_ok = VPNManager.look_ip(args.VPNdata)
                if not is_ip_ok:
                    if args.Emaildata:
                        # Send the email to clients in case of a change
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


if __name__ == '__main__':
    main()