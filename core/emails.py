from typing import List, IO, AnyStr

from django.core.mail import EmailMessage, send_mail
from django.core.mail import EmailMultiAlternatives


class Attachment():
    def __init__(self, filename: str, data: IO[AnyStr], mime: str):
        self.filename = filename
        self.data = data
        self.mime = mime


def send_email(recipients: List[str], subject: str, text_content: str = 'No plain text version privided.', html_content: str = None, attachments: List[Attachment] = None):
    # Create an Email object
    # email = EmailMessage(subject=subject, from_email='bob@tim.com', body=text_content, to=recipients)
    email = EmailMultiAlternatives(subject=subject, from_email='bob@tim.com', body=text_content, to=recipients)
    # Fill out the email with appropriate things
    if html_content:
        email.attach_alternative(html_content, 'text/html')
    # Attach any attachments
    if attachments:
        for attachment in attachments:
            email.attach(attachment.filename, attachment.data, attachment.mime)
    # send the email
    email.send(fail_silently=False)