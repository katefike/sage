import requests
from requests.exceptions import HTTPError

from loguru import logger

from . import ENV

logger.add(sink="debug.log", level="INFO")

DO_API_BASE_URL = ENV["DO_API_BASE_URL"]
HEADERS = {"Authorization": f"Bearer {ENV['DO_API_TOKEN']}"}


def main():
    droplet_id = get_droplet_id()
    # TODO: Get droplet with target name
    # droplet name and firewall name needs parameratized
    response = post_add_droplet_to_firewall(droplet_id)


def get_droplet_id() -> int:
    try:
        url = DO_API_BASE_URL + "droplets?name=sage.ephem"
        response = requests.get(url, headers=HEADERS)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        logger.critical(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logger.critical(f"Other error occurred: {err}")
    else:
        json_response = response.json()
        droplets = json_response.get("droplets")
        droplet = droplets[0]
        return droplet.get("id")


def post_add_droplet_to_firewall(droplet_id: int):
    pass


if __name__ == "__main__":  # pragma: no cover
    main()
