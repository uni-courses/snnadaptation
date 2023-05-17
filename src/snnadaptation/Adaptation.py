"""Contains experiment settings."""
# pylint: disable=R0801

import hashlib
import json

from typeguard import typechecked


# pylint: disable=R0903
class Adaptation:
    """Specification of a simulated radiation model: where neuron currents can
    decrease/increase randomly (if they are excited by a incoming
    radiation.)"""

    @typechecked
    def __init__(
        self,
        adaptation_type: str,
        redundancy: int,
    ) -> None:
        self.adaptation_type: str = adaptation_type
        if self.adaptation_type not in ["redundancy", "population"]:
            raise NotImplementedError(
                f"Error, {self.adaptation_type} not supported."
            )
        self.redundancy: int = redundancy
        if self.redundancy < 1:
            raise ValueError(
                "Error, redundancy must be equal to, or larger than 1."
            )

    @typechecked
    def get_hash(
        self,
    ) -> str:
        """Returns a unique hash of the object."""
        unique_id = str(
            hashlib.sha256(
                # json.dumps(sorted(some_config.__dict__)).encode("utf-8")
                json.dumps(f"{self.adaptation_type}_{self.redundancy}").encode(
                    "utf-8"
                )
            ).hexdigest()
        )
        return unique_id
