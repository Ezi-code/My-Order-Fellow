"""local settings for myOrderFellow project."""

from .base import *  # noqa F403

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-m5!8_e4vop+j#!_-c@vl)oylv56bt9bz=!*-#7u(r$9s!uc4(8"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa F405
    }
}

STATIC_URL = "static/"
