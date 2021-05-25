import os.path

import pytest

from nre_utils import ebmlite_utils


@pytest.mark.parametrize(
    "filename, config_id, element_name, expt_result",
    [
        # "Segments" attributes
        (os.path.join("tests", "ActTest_009.IDE"), 0x1CFF7F, "UIntValue", [1]),
        (os.path.join("tests", "test1.IDE"), 0x1CFF7F, "UIntValue", []),
        # "Device name" attributes
        (os.path.join("tests", "ActTest_009.IDE"), 0x8FF7F, "TextValue", []),
        (
            os.path.join("tests", "test1.IDE"),
            0x8FF7F,
            "TextValue",
            ["Steve's Microphone"],
        ),
    ],
)
def test_iter_config_attrs(filename, config_id, element_name, expt_result):
    calc_result = list(
        ebmlite_utils.iter_config_attrs(
            filename,
            config_id,
            element_name,
        )
    )
    assert calc_result == expt_result
