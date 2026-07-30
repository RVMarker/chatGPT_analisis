import logging

from pathlib import Path

import yaml


def configure_logging():

    config_file = Path("config") / "logging.yaml"

    if not config_file.exists():

        logging.basicConfig(level=logging.INFO)

        return

    with open(config_file, encoding="utf-8") as f:

        config = yaml.safe_load(f)

    import logging.config

    logging.config.dictConfig(config)