"""Contains experiment settings."""
# pylint: disable=R0801
from typing import Dict

from snncompare.exp_config.Supported_experiment_settings import (
    Supported_experiment_settings,
)
from typeguard import typechecked


class Adaptations_settings:
    """Stores all used adaptation settings."""

    # pylint: disable=R0903

    @typechecked
    def __init__(
        self,
    ) -> None:

        self.without_adaptation: Dict = {
            "None": [],
        }

        self.with_adaptation = {
            "redundancy": [
                1.0,
                3.0,
                5.0,
            ],
        }

        self.with_and_without_adaptation = {
            "None": [],
            "redundancy": [
                1.0,
            ],
        }


class Radiation_settings:
    """Stores all used radiation settings."""

    # pylint: disable=R0903

    @typechecked
    def __init__(
        self,
    ) -> None:
        self.without_radiation: Dict = {
            "None": [],
        }
        self.with_radiation = {
            "neuron_death": [
                # 0.01,
                # 0.05,
                # 0.1,
                0.2,
                0.25,
            ],
        }
        self.with_and_without_radiation = {
            "None": [],
            "neuron_death": [
                0.01,
                0.05,
                0.1,
                0.2,
                0.25,
            ],
        }


adaptation_settings = Adaptations_settings()
radiation_settings = Radiation_settings()
supported_settings = Supported_experiment_settings()
