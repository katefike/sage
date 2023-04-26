import requests
from loguru import logger
from requests.exceptions import HTTPError

from . import ENV

logger.add(sink="debug.log", level="INFO")

DO_API_BASE_URL = ENV["DO_API_BASE_URL"]
HEADERS = {
    "Authorization": f"Bearer {ENV['DO_API_TOKEN']}",
    "Content-Type": "application/json",
}
NAME = ENV["EPHEM_NAME"]


def main():
    droplet_id = get_droplet_id()
    # TODO: Get droplet with target name
    # droplet name and firewall name needs parameratized
    firewall_id = get_firewall_id()
    add_droplet_to_firewall(droplet_id, firewall_id)


def get_droplet_id() -> int:
    try:
        url = DO_API_BASE_URL + f"droplets?name={NAME}"
        response = requests.get(url, headers=HEADERS)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as e:
        logger.critical(f"HTTP error occurred: {e}")
    except Exception as e:
        logger.critical(f"Other error occurred: {e}")
    else:
        json_response = response.json()
        droplets = json_response.get("droplets")
        droplet = droplets[0]
        return droplet.get("id")


def get_firewall_id() -> str:
    try:
        url = DO_API_BASE_URL + "firewalls"
        response = requests.get(url, headers=HEADERS)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as e:
        logger.critical(f"HTTP error occurred: {e}")
    except Exception as e:
        logger.critical(f"Other error occurred: {e}")
    else:
        json_response = response.json()
        firewalls = json_response.get("firewalls")
        for firewall in firewalls:
            if firewall.get("name") == NAME:
                return firewall.get("id")


def add_droplet_to_firewall(droplet_id: int, firewall_id: str):
    try:
        url = DO_API_BASE_URL + f"firewalls/{firewall_id}/droplets"
        body = {"droplet_ids": [droplet_id]}
        response = requests.post(url, headers=HEADERS, json=body)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as e:
        logger.critical(f"HTTP error occurred: {e}")
    except Exception as e:
        logger.critical(f"Other error occurred: {e}")
    else:
        if response.status_code != 204:
            logger.critical(
                f"Response code other than 204 was returned: {response.status_code}"
            )


if __name__ == "__main__":  # pragma: no cover
    main()
