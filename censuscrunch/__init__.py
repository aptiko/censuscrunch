import importlib
import os

__version__ = "DEV"
VERSION = __version__  # synonym


def set_django_settings_module():
    # The default value for settings is censuscrunch_project.settings.local if such a
    # thing exists, otherwise it's censuscrunch_project_project.settings.base, which
    # always exists.
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        importlib.util.find_spec("censuscrunch_project.settings.local")
        and "censuscrunch_project.settings.local"
        or "censuscrunch_project.settings.base",
    )
