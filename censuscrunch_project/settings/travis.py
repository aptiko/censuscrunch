from .base import *  # NOQA

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "censuscrunch",
        "USER": "postgres",
        "HOST": "localhost",
        "PORT": 5432,
    }
}
