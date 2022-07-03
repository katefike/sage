import logging

LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    filename="sage.log",
    encoding="utf-8",
    format="%(asctime)s:%(levelname)s:%(message)s",
)
