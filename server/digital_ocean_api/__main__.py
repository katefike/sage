import requests
from loguru import logger

from . import ENV

logger.add(sink="debug.log", level="INFO")


def main():
    response = get_list_all_droplets()
    # TODO: Get droplet with target name
    # droplet name and firewall name needs parameratized
    droplet_id = 1111111
    response = post_add_droplet_to_firewall(droplet_id)


def get_list_all_droplets():
    pass


def post_add_droplet_to_firewall():
    pass


if __name__ == "__main__":  # pragma: no cover
    main()
