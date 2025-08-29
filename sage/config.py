import os
import pathlib

from dotenv import dotenv_values


if os.environ.get("ISDEV") == "True":
    ISDEV = True
    ENV_FILE = "/.env-example"
else:  # pragma: no cover
    ISDEV = False
    ENV_FILE = "/.env"

APP_ROOT = str(pathlib.Path(__file__).parent.parent)

ENV = dotenv_values(APP_ROOT + ENV_FILE)
ENV["ISDEV"] = ISDEV

# Banks config is cached after the first access
# The import is in a weird spot to avoid circular import
_BANKS_CONFIG = None
def BANKS_CONFIG():
    global _BANKS_CONFIG
    if _BANKS_CONFIG is None:
        from sage.db.banks import get_banks_config
        _BANKS_CONFIG = get_banks_config()
    return _BANKS_CONFIG
