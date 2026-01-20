"""
ASGI config for myOrderFellow project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

DEBUG = os.environ.get("DJANGO_DEBUG", "True")

if DEBUG:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myOrderFellow.settings.local")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myOrderFellow.settings.production")

application = get_asgi_application()
