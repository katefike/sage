import pathlib

from dotenv import dotenv_values

APP_ROOT = str(pathlib.Path(__file__).parent.parent)
ENV = dotenv_values(APP_ROOT + "/.env")
