import json
import logging
import time

import requests
import ipaddress


def get_server_setting(file_path):
    """Load server settings from a specified JSON file.

    Args:
        file_path (str): Path to the JSON file containing server settings.

    Returns:
        dict: Server settings loaded from the file.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def get_public_ip():
    """Fetch the public IP of the server using an external service.

    Returns:
        str: The public IP address if successful, None otherwise.
    """
    try:
        response = requests.get('https://httpbin.org/ip')
        return response.json()['origin'].split(',')[0]
    except Exception as e:
        logging.error(f"Failed to retrieve public IP. Error: {e}")
        return None


def ip_comparison(file_path: str, current_ip: str):
    try:
        if not ipaddress.ip_address(current_ip) or current_ip is None:
            return None

        with open(file_path, 'r') as file:
            data = json.load(file)
        if data is None:
            logging.error('No file for the server IP')
            return None

        if data['server_ip'] == current_ip:
            return True

        data['server_ip'] = current_ip

        with open(file_path, 'w') as file:
            data['server_ip'] = current_ip
            json.dump(data, file)
            logging.info('Changing IP address')

        return False
    except:
        logging.error('Ip looking section crashed')
        return None


def look_ip(file_path):
    """Check if the current public IP matches the IP saved in the settings.

    Args:
        file_path (str): Path to the JSON file containing server settings.

    Returns:
        bool: True if the IPs match, False otherwise.
    """
    current_ip = get_public_ip()
    return ip_comparison(file_path, current_ip)


