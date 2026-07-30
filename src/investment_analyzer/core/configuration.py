from pathlib import Path

import yaml


class Configuration:

    def __init__(self, config_directory: str = "config"):

        self.directory = Path(config_directory)

        self.config = self._load("config.yaml")

        self.providers = self._load("providers.yaml")

        self.weights = self._load("weights.yaml")

        self.profiles = self._load("profiles.yaml")

        self.scoring = self._load("scoring.yaml")

        self.logging = self._load("logging.yaml")

        self.report = self._load("report.yaml")

    def _load(self, filename):

        file = self.directory / filename

        if not file.exists():

            raise FileNotFoundError(file)

        with open(file, encoding="utf-8") as f:

            return yaml.safe_load(f)