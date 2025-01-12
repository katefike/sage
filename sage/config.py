import os
import pathlib
import yaml

from dotenv import dotenv_values


if os.environ.get("ISDEV") == "True":
    ISDEV = True
    ENV_FILE = "/.env-example"
    BANKS_CONFIG_FILE = "/banks_config-example.yml"
else:  # pragma: no cover
    ISDEV = False
    ENV_FILE = "/.env"
    BANKS_CONFIG_FILE = "/banks_config.yml"

APP_ROOT = str(pathlib.Path(__file__).parent.parent)

ENV = dotenv_values(APP_ROOT + ENV_FILE)
ENV["ISDEV"] = ISDEV

with open(APP_ROOT + BANKS_CONFIG_FILE, 'r') as file:
    BANKS_CONFIG = yaml.safe_load(file)

print(BANKS_CONFIG)

