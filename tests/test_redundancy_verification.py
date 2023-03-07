"""Tests whether the snn MDSA algorithm results equal those of the
default/Neumann implementation.

TODO: Resolve duplicate code between:
verify_redundancy_settings_for_exp_config
and:
verify_redundancy_settings_for_run_config
and make sure they both work properly.
"""
# pylint: disable=R0801


from typing import Dict, List

from typeguard import typechecked

from snnadaptation.redundancy.verify_redundancy_settings import (
    verify_redundancy_settings_for_exp_config,
)

# from ...tests.sparse.MDSA.test_snn_results
# import Test_mdsa_snn_results
from tests.test_snn_results_adaptation import Test_mdsa_snn_results


class Test_invalid_redundancy_is_caught(Test_mdsa_snn_results):
    """Verifies redundancy settings are tested correctly."""

    def __init__(self, *args, **kwargs) -> None:  # type:ignore[no-untyped-def]
        super(Test_mdsa_snn_results, self).__init__(*args, **kwargs)
        # Generate default experiment config.
        self.create_exp_config()

    @typechecked
    def test_verify_redundancy_settings_catches_invalid_redundancy(
        self,
    ) -> None:
        """Tests whether the verify_redundancy_settings function throws an
        error if an invalid redundancy is passed into it."""
        invalid_redundancies = [-2, -1, 0, 2, 4, 6]
        for invalid_redundancy in invalid_redundancies:
            # Modify configuration to include adaptation.
            adaptation_settings: Dict[str, List[int]] = {
                "redundancy": [invalid_redundancy]
            }

            with self.assertRaises(ValueError) as context:
                print(f"adaptation_settings={adaptation_settings}")
                verify_redundancy_settings_for_exp_config(
                    adaptation=adaptation_settings
                )

            if invalid_redundancy < 1:
                self.assertTrue(
                    "Error, redundancy should be 1 or larger."
                    in str(context.exception)
                )
            else:
                self.assertTrue(
                    "Error, redundancy should be odd integer."
                    in str(context.exception)
                )

    @typechecked
    def test_verify_redundancy_settings_allows_valid_redundancy_values(
        self,
    ) -> None:
        """Tests whether the verify_redundancy_settings function allows valid
        redundancy values to pass."""
        invalid_redundancies = [1, 3, 5, 7]
        for invalid_redundancy in invalid_redundancies:
            # Modify configuration to include adaptation.
            adaptation_settings: Dict[str, List[int]] = {
                "redundancy": [invalid_redundancy]
            }

            verify_redundancy_settings_for_exp_config(
                adaptation=adaptation_settings
            )

    @typechecked
    def test_verify_redundancy_settings_allows_none_adaptation(
        self,
    ) -> None:
        """Tests whether the verify_redundancy_settings function allows an
        adaptation setting of None to pass."""
        verify_redundancy_settings_for_exp_config(adaptation=None)

    @typechecked
    def test_invalid_redundancy_settings_are_caught(
        self,
    ) -> None:
        """Tests whether the verify_redundancy_settings function throws an
        error if an invalid redundancy is passed into it."""
        invalid_redundancies = [-2, -1, 0, 2, 4, 6]
        for invalid_redundancy in invalid_redundancies:
            # Modify configuration to include adaptation.
            self.mdsa_settings.adaptations = {
                "redundancy": [invalid_redundancy]
            }
            # adaptation_settings: Dict[str, List[int]] = {
            #    "redundancy": [invalid_redundancy]
            # }

            with self.assertRaises(ValueError) as context:
                # Perform test.
                self.helper(self.mdsa_settings)

            if invalid_redundancy < 1:
                self.assertTrue(
                    "Error, redundancy should be 1 or larger."
                    in str(context.exception)
                )
            else:
                self.assertTrue(
                    "Error, redundancy should be odd integer."
                    in str(context.exception)
                )
