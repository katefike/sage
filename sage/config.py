import os
import pathlib

from dotenv import dotenv_values

if os.environ.get("ISDEV") == "True":
    ISDEV = True
    ENV_FILE = "/.env-example"
else:
    ISDEV = False
    ENV_FILE = "/.env"

APP_ROOT = str(pathlib.Path(__file__).parent.parent)

ENV = dotenv_values(APP_ROOT + ENV_FILE)

ENV["ISDEV"] = ISDEV
