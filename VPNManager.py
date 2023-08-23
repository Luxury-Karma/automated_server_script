import json
import logging
import requests


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


def look_ip(file_path):
    """Check if the current public IP matches the IP saved in the settings.

    Args:
        file_path (str): Path to the JSON file containing server settings.

    Returns:
        bool: True if the IPs match, False otherwise.
    """
    current_ip = get_public_ip()
    with open(file_path, 'r') as file:
        data = json.load(file)
    if data['server_ip'] == current_ip:
        return True
    else:
        data['server_ip'] = current_ip
        with open(file_path, 'w') as file:
            data['server_ip'] = current_ip
            json.dump(data, file)
        return False
