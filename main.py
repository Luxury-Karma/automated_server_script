import json
import requests
import logging
import docker
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


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
            return json.load(setting)
    except:
        logging.error('Failed to open server settings. Initialising the settings')
        init_setting: dict = {
            'server_public_ip': get_public_ip() if get_public_ip() else '169.254.0.1',
            'server_local_ip': '10.0.0.1',
            'vpn_container_name': 'OpenVPN_server',
            'vpn_user_name': 'user',
            'vpn_user_password': 'password',
            'server_email': 'server_email@gmail.com',
            'server_email_password': 'password'
        }
        with open('server_setting.json', 'w') as setting:
            json.dump(init_setting, setting)
        return init_setting


def is_container_running(container_name_or_id:str) -> bool:
    client = docker.from_env()
    try:
        container = client.containers.get(container_name_or_id)
        return container.status == 'running'
    except:
        logging.error('Error in the container research')
        return False


def create_vpn_container(container_emplacement: str, port: str, user_name: str, user_password: str,
                         server_local_ip: str, server_name: str):
    client = docker.from_env()

    # Pull the required image
    client.images.pull('bogem/ftp')

    # Volume mapping
    volume_mapping = {container_emplacement: {'bind': '/home/vsftpd', 'mode': 'rw'}}

    # Environment variables
    environment = {
        'VPN_USER': user_name,
        'VPN_PASS': user_password,
        'PASV_ADDRESS': server_local_ip
    }

    # Port mapping
    ports = {f'{port}/tcp': port}

    # Create the container
    container = client.containers.create(
        image='bogem/ftp',
        name=server_name,
        volumes=volume_mapping,
        environment=environment,
        ports=ports,
        restart_policy={"Name": "always"}
    )

    # Start the container
    container.start()

    print(f'{server_name} created and started.')


def send_email(subject, body, to_email,server_email: str, server_password:str, attachment_path=None):
    try:
        """
        Main usage will be to send the new login files to the user once the docker is created
        :param subject: what the email is about
        :param body: the text inside the email
        :param to_email: to who it is send
        :param server_email: what is the server's email
        :param server_password: what is the server's email's password
        :param attachment_path: where is the file to send
        :return: None
        """
        # Email & Password used for sending the email
        email_user = server_email  # need to be a gmail in this exemple
        email_password = server_password

        # Setting up the MIME
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = to_email
        msg['Subject'] = subject

        # Body of the email
        msg.attach(MIMEText(body, 'plain'))

        # Attachment
        if attachment_path:
            filename = attachment_path.split("/")[-1]
            attachment = open(attachment_path, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= "+filename)
            msg.attach(part)

        # Start the server and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_password)
        server.sendmail(email_user, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        logging.error(f'The email for {to_email} could not be sent, error {e}')


def main():
    # Setup logging
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    while True:
        current_setting = get_server_setting()
        if is_container_running(current_setting['vpn_container_name']):
            if current_setting['server_public_ip'] != get_public_ip():
                # need to create a new container with the new ip
                pass
        else:
            # need to create the container
            pass
        time.sleep(3600)  # Sleep for 1 hour (3600 seconds)


if __name__ == '__main__':
    main()


# Example usage
create_vpn_container("/path/to/container_emplacement", "21", "username", "password", "192.168.1.10", "my_VPN_server")
