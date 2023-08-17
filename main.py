import json

import requests
import logging


def get_public_ip():
    try:
        answer = requests.get('https://httpbin.org/ip')
        return answer
    except:
        logging.error("Failed to retrieve public IP")
        return None

def get_server_setting() -> dict:
    try:
        with open('server_setting.json', 'r') as setting:
            json.load(setting)
    except:
        logging.error('Failed to open server settings. Initialising the settings')
        init_setting: dict = {
            'server_public_ip': get_public_ip() if get_public_ip() else '169.254.0.1'
        }

