"""Verifies the redundancy settings are valid."""
from typing import Dict, Union

from typeguard import typechecked


@typechecked
def verify_redundancy_settings_for_exp_setts(
    # adaptation: Union[None, Dict[str, List[int]]],
    adaptation: Union[None, Dict],
) -> None:
    """Verifies the redundancy settings are presented in the right format, and
    that they contain valid values."""
    print(f"type:adaptation={type(adaptation)}")
    if isinstance(adaptation, Dict):
        if "redundancy" in adaptation.keys():
            for redundancy in adaptation["redundancy"]:
                if redundancy < 1:
                    raise ValueError(
                        "Error, redundancy should be 1 or larger."
                    )
                if redundancy % 2 == 0:
                    raise ValueError(
                        "Error, redundancy should be odd integer."
                    )

        else:
            raise KeyError(
                "Error, no valid redundancy setting found in:"
                + f"{adaptation.keys()}"
            )


@typechecked
def verify_redundancy_settings_for_run_config(
    # adaptation: Union[None, Dict[str, List[int]]],
    adaptation: Union[None, Dict],
) -> None:
    """Verifies the redundancy settings are presented in the right format, and
    that they contain valid values."""
    print(f"type:adaptation={type(adaptation)}")
    if isinstance(adaptation, Dict):
        if "redundancy" in adaptation.keys():
            if adaptation["redundancy"] < 1:
                raise ValueError("Error, redundancy should be 1 or larger.")
            if adaptation["redundancy"] % 2 == 0:
                raise ValueError("Error, redundancy should be odd integer.")

        else:
            raise KeyError(
                "Error, no valid redundancy setting found in:"
                + f"{adaptation.keys()}"
            )
