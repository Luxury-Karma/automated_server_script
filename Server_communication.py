import json
import logging
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders


def get_email_settings(file_path):
    """Load email settings from a specified JSON file.

    Args:
        file_path (str): Path to the JSON file containing email settings.

    Returns:
        dict: Email settings loaded from the file.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def send_email(subject, body, to_email, server_email, server_password, attachment_path=None):
    """Send an email using the specified settings and content.

    Args:
        subject (str): Subject of the email.
        body (str): Body/content of the email.
        to_email (str): Recipient's email address.
        server_email (str): Sender's email address.
        server_password (str): Password for the sender's email account.
        attachment_path (str, optional): Path to a file to be attached to the email. Defaults to None.

    Returns:
        None
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = server_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        if attachment_path:
            filename = attachment_path.split("/")[-1]
            attachment = open(attachment_path, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename={filename}")
            msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(server_email, server_password)
        server.sendmail(server_email, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        logging.error(f'The email for {to_email} could not be sent. Error: {e}')
