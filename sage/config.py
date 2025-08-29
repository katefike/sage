import os
import pathlib

from dotenv import dotenv_values
from sage.db.banks import get_banks_config

if os.environ.get("ISDEV") == "True":
    ISDEV = True
    ENV_FILE = "/.env-example"
else:  # pragma: no cover
    ISDEV = False
    ENV_FILE = "/.env"

APP_ROOT = str(pathlib.Path(__file__).parent.parent)

ENV = dotenv_values(APP_ROOT + ENV_FILE)
ENV["ISDEV"] = ISDEV

BANKS_CONFIG = get_banks_config()
