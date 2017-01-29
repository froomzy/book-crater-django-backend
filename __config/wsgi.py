"""
WSGI config for bookcarterbackend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("BOOK_CRATER_SETTINGS_MODULE", "__config.settings.production")

application = get_wsgi_application()
