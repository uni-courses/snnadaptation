"""Verifies the redundancy settings are valid."""
from typing import Dict, Union

from typeguard import typechecked

from snnadaptation.Adaptation import Adaptation


@typechecked
def verify_redundancy_settings_for_exp_config(
    *,
    adaptation: Union[None, Adaptation],
) -> None:
    """Verifies the redundancy settings are presented in the right format, and
    that they contain valid values."""

    if isinstance(adaptation, Dict):
        if "redundancy" in adaptation.keys():
            for redundancy in adaptation["redundancy"]:
                if redundancy < 2:
                    raise ValueError(
                        "Error, redundancy should be 2 or larger."
                    )
                if redundancy % 2 == 1:
                    raise ValueError(
                        "Error, redundancy should be even integer."
                    )

        else:
            raise KeyError(
                "Error, no valid redundancy setting found in:"
                + f"{adaptation.keys()}"
            )


@typechecked
def verify_redundancy_settings_for_run_config(
    *,
    adaptation: Union[None, Adaptation],
) -> None:
    """Verifies the redundancy settings are presented in the right format, and
    that they contain valid values."""

    if isinstance(adaptation, Dict):
        if "redundancy" in adaptation.keys():
            if adaptation["redundancy"] < 2:
                raise ValueError("Error, redundancy should be 2 or larger.")
            if adaptation["redundancy"] % 2 == 1:
                raise ValueError("Error, redundancy should be even integer.")

        else:
            raise KeyError(
                "Error, no valid redundancy setting found in:"
                + f"{adaptation.keys()}"
            )
