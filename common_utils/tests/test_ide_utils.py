import os
import warnings

import pytest
import idelib

from nre_utils import ide_utils


def test_ChannelStruct():
    with idelib.importFile(os.path.join("tests", "test3.IDE")) as ds:
        calc_result = ide_utils.ChannelStruct(ds.channels[8], [0, 1, 2])
        expt_result = (
            ds.channels[8],
            [0, 1, 2],
            ds.channels[8].getSession(),
            ds.channels[8].getSession().getSampleRate(),
            ds.channels[8].subchannels[0].units,
        )
        assert calc_result == expt_result[:2]
        assert calc_result.eventarray == expt_result[2]
        assert calc_result.fs == expt_result[3]
        assert calc_result.units == expt_result[4]


def test_chs_by_utype():
    def sorting_key(x):
        return x[0], x[1][0].id

    with idelib.importFile(os.path.join("tests", "test3.IDE")) as ds:
        calc_result = sorted(ide_utils.chs_by_utype(ds), key=sorting_key)
        expt_result = [
            ("acc", (ds.channels[8], [0, 1, 2])),
            ("acc", (ds.channels[80], [0, 1, 2])),
            ("gyr", (ds.channels[70], [0, 1, 2, 3])),
            ("gyr", (ds.channels[84], [0, 1, 2])),
            ("mic", (ds.channels[8], [3])),
            ("pre", (ds.channels[36], [0])),
            ("pre", (ds.channels[59], [0])),
            ("tmp", (ds.channels[36], [1])),
            ("tmp", (ds.channels[59], [1])),
        ]
        assert calc_result == expt_result


@pytest.mark.parametrize(
    "filename",
    [
        os.path.join("tests", "test3.IDE"),  # basic channels (accel, pre/tmp, etc)
        os.path.join("tests", "test4.IDE"),  # GPS channels
        os.path.join("tests", "SAM_pockets.IDE"),  # light channels
    ],
)
def test_chs_by_utype_warnings(filename):
    """Confirm that `chs_by_utype` raises no warnings."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("error")

        with idelib.importFile(filename) as ds:
            _ = list(ide_utils.chs_by_utype(ds))


def test_dict_groups():
    with idelib.importFile(os.path.join("tests", "test3.IDE")) as ds:
        calc_result = ide_utils.dict_groups(
            iter(
                [
                    ("acc", (ds.channels[8], [0, 1, 2])),
                    ("acc", (ds.channels[80], [0, 1, 2])),
                    ("gyr", (ds.channels[70], [0, 1, 2, 3])),
                    ("gyr", (ds.channels[84], [0, 1, 2])),
                    ("mic", (ds.channels[8], [3])),
                    ("pre", (ds.channels[36], [0])),
                    ("pre", (ds.channels[59], [0])),
                    ("tmp", (ds.channels[36], [1])),
                    ("tmp", (ds.channels[59], [1])),
                ]
            )
        )
        expt_result = {
            "acc": [
                (ds.channels[8], [0, 1, 2]),
                (ds.channels[80], [0, 1, 2]),
            ],
            "mic": [
                (ds.channels[8], [3]),
            ],
            "gyr": [
                (ds.channels[70], [0, 1, 2, 3]),
                (ds.channels[84], [0, 1, 2]),
            ],
            "pre": [
                (ds.channels[36], [0]),
                (ds.channels[59], [0]),
            ],
            "tmp": [
                (ds.channels[36], [1]),
                (ds.channels[59], [1]),
            ],
        }

        assert calc_result == expt_result


def test_dict_chs_best():
    with idelib.importFile(os.path.join("tests", "test3.IDE")) as ds:
        calc_result = ide_utils.dict_chs_best(
            [
                ("acc", ide_utils.ChannelStruct(ds.channels[8], [0, 1, 2])),
                ("mic", ide_utils.ChannelStruct(ds.channels[8], [3])),
                ("acc", ide_utils.ChannelStruct(ds.channels[80], [0, 1, 2])),
                ("gyr", ide_utils.ChannelStruct(ds.channels[84], [0, 1, 2])),
                ("pre", ide_utils.ChannelStruct(ds.channels[36], [0])),
                ("tmp", ide_utils.ChannelStruct(ds.channels[36], [1])),
                ("gyr", ide_utils.ChannelStruct(ds.channels[70], [0, 1, 2, 3])),
                ("pre", ide_utils.ChannelStruct(ds.channels[59], [0])),
                ("tmp", ide_utils.ChannelStruct(ds.channels[59], [1])),
            ]
        )
        expt_result = {
            "acc": (ds.channels[8], [0, 1, 2]),
            "mic": (ds.channels[8], [3]),
            "gyr": (ds.channels[84], [0, 1, 2]),
            "pre": (ds.channels[59], [0]),
            "tmp": (ds.channels[59], [1]),
        }
        assert calc_result == expt_result


def test_get_ch_type_best():
    with idelib.importFile(os.path.join("tests", "test3.IDE")) as ds:
        calc_result = ide_utils.get_ch_type_best(ds, "acc")
        expt_result = (ds.channels[8], [0, 1, 2])

        assert calc_result == expt_result


def test_get_ch_type_best_exception():
    """Test failure mode when recording has no acceleration channel."""
    with idelib.importFile(os.path.join("tests", "test4.IDE")) as ds:
        with pytest.raises(ide_utils.NoChannelException):
            _ = ide_utils.get_ch_type_best(ds, "acc")
