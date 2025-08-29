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

# Banks config will be loaded when needed
_BANKS_CONFIG = None


def get_banks_config():
    """Get banks configuration from database with caching."""
    global _BANKS_CONFIG
    if _BANKS_CONFIG is None:
        from sage.db.banks import get_banks_config as load_banks_config
        _BANKS_CONFIG = load_banks_config()
    return _BANKS_CONFIG


# For backward compatibility, provide BANKS_CONFIG as a function call
def BANKS_CONFIG():
    """Get banks configuration from database with caching."""
    return get_banks_config()
