from typing import List, IO, AnyStr

from django.conf import settings
from django.core.mail import EmailMultiAlternatives  # type: ignore


class Attachment:
    def __init__(self, filename: str, data: IO, mime: str) -> None:
        self.filename = filename  # type: str
        self.data = data  # type: IO
        self.mime = mime  # type: str


def send_email(recipients: List[str], subject: str, text_content: str = 'No plain text version provided.', html_content: str = None, attachments: List[Attachment] = None):
    email = EmailMultiAlternatives(subject=subject, from_email=settings.DEFAULT_FROM_EMAIL, body=text_content, to=recipients)
    if html_content:
        email.attach_alternative(html_content, 'text/html')
    if attachments:
        for attachment in attachments:
            email.attach(attachment.filename, attachment.data, attachment.mime)
    email.send(fail_silently=False)
