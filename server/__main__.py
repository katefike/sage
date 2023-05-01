import pathlib

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
EPHEM_SSH_KEY_PUB = ENV["EPHEM_SSH_KEY_PUB"]
APP_ROOT = str(pathlib.Path(__file__).parent.parent.parent)


def main():
    create_account_ssh_keys()
    droplet_id = create_droplet()
    firewall_id = create_firewall(droplet_id)
    add_droplet_to_firewall(droplet_id, firewall_id)


def create_account_ssh_keys():
    # TODO: If this is being used for the ephemeral server, if the key already exists, don't create a new one
    try:
        url = DO_API_BASE_URL + "account/keys"
        body = {"public_key": f"{EPHEM_SSH_KEY_PUB}", "name": "Sage Local"}
        response = requests.post(url, headers=HEADERS, json=body)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as e:
        logger.critical(f"HTTP error occurred: {e.response.text}")
    except Exception as e:
        logger.critical(f"Other error occurred: {e}")
    else:
        json_response = response.json()
        # TODO: Get id


def create_droplet() -> int:
    try:
        url = DO_API_BASE_URL + "droplets"
        body = {
            "name": NAME,
            "region": "nyc1",
            "size": "s-1vcpu-1gb",
            "image": "ubuntu-22-04-x64",
            # FIXME: Add ssh key when create_account_ssh_keys gets fixed
            # "ssh_keys": [289794, "3b:16:e4:bf:8b:00:8b:b8:59:8c:a9:d3:f0:19:fa:45"],
        }
        response = requests.post(url, headers=HEADERS, json=body)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as e:
        logger.critical(f"HTTP error occurred: {e.response.text}")
    except Exception as e:
        logger.critical(f"Other error occurred: {e}")
    else:
        if response.status_code != 202:
            logger.critical(
                f"Response code other than 202 was returned: {response.status_code}"
            )
        json_response = response.json()
        droplet = json_response.get("droplet")
        return droplet.get("id")


def create_firewall(droplet_id):
    try:
        url = DO_API_BASE_URL + "firewalls"
        body = {
            "name": NAME,
            "inbound_rules": [
                {
                    "protocol": "tcp",
                    "ports": "22",
                    "sources": {"addresses": ["0.0.0.0/0", "::/0"]},
                },
                {
                    "protocol": "tcp",
                    "ports": "80",
                    "sources": {"addresses": ["0.0.0.0/0", "::/0"]},
                },
                {
                    "protocol": "tcp",
                    "ports": "22",
                    "sources": {"addresses": ["0.0.0.0/0", "::/0"]},
                },
            ],
            "outbound_rules": [
                {
                    "protocol": "tcp",
                    "ports": "587",
                    "destinations": {"addresses": ["0.0.0.0/0", "::/0"]},
                },
            ],
            # "droplet_ids": [droplet_id],
        }
        response = requests.post(url, headers=HEADERS, json=body)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as e:
        logger.critical(f"HTTP error occurred: {e.response.text}")
    except Exception as e:
        logger.critical(f"Other error occurred: {e}")
    else:
        if response.status_code != 202:
            logger.critical(
                f"Response code other than 202 was returned: {response.status_code}"
            )


def get_droplet_id() -> int:
    # This isn't being used and can probably be deleted
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
    # This isn't being used and can probably be deleted
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
