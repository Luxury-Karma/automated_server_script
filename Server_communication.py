import json
import smtplib
import logging
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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


def set_email_setting(path_to_file: str, email: str, e_password : str):
    setting = {
        'server_email': email,
        'server_email_password': e_password
    }


def get_email_settings(path_to_file: str) -> dict:
    with open(path_to_file, 'r') as f:
        return json.load(f)