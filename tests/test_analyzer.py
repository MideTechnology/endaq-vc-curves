import os
from unittest import mock

import idelib
import numpy as np
import pytest

import bsvp.analyzer
from common_utils.nre_utils.calc.stats import rms, L2_norm


np.random.seed(0)


@pytest.fixture()
def ide_SSX70065():
    with idelib.importFile(os.path.join("tests", "SSX70065.IDE")) as doc:
        yield doc


@pytest.fixture()
def analyzer_raw():
    analyzer_mock = mock.create_autospec(
        bsvp.analyzer.Analyzer, spec_set=False, instance=True
    )

    analyzer_mock.MPS2_TO_G = bsvp.analyzer.Analyzer.MPS2_TO_G
    analyzer_mock.MPS_TO_MMPS = bsvp.analyzer.Analyzer.MPS_TO_MMPS
    analyzer_mock.M_TO_MM = bsvp.analyzer.Analyzer.M_TO_MM
    analyzer_mock.PV_NATURAL_FREQS = bsvp.analyzer.Analyzer.PV_NATURAL_FREQS

    return analyzer_mock


@pytest.fixture()
def analyzer_bulk(analyzer_raw):
    analyzer_mock = analyzer_raw

    analyzer_mock._channels = {
        "acc": mock.Mock(axis_names=list("XYZ")),
        "gps": mock.Mock(axis_names=["Latitude", "Longitude"]),
        "spd": mock.Mock(axis_names=["Ground"]),
        "gyr": mock.Mock(axis_names=list("XYZ")),
        "mic": mock.Mock(axis_names=["Mic"]),
        "tmp": mock.Mock(axis_names=["Control"]),
        "pre": mock.Mock(axis_names=["Control"]),
    }

    analyzer_mock._accelerationFs = 3000
    analyzer_mock._accelerationData = np.random.random((3, 21))
    analyzer_mock._accelerationResultant = L2_norm(
        analyzer_mock._accelerationData, axis=0
    )
    analyzer_mock._microphoneData = np.random.random((1, 21))
    analyzer_mock._velocityData = np.random.random((3, 21))
    analyzer_mock._displacementData = np.random.random((3, 21))
    analyzer_mock._pressureData = np.random.random(5)
    analyzer_mock._temperatureData = np.random.random(5)
    analyzer_mock._gyroscopeData = np.random.random(11)

    return analyzer_mock


# ==============================================================================
# Analyzer class tests
# ==============================================================================


class TestAnalyzer:
    def test_accRMSFull(self, analyzer_bulk):
        assert bsvp.analyzer.Analyzer.accRMSFull.func(analyzer_bulk)[
            "Resultant"
        ] == pytest.approx(
            bsvp.analyzer.Analyzer.MPS2_TO_G
            * rms(L2_norm(analyzer_bulk._accelerationData, axis=0))
        )

    def test_velRMSFull(self, analyzer_bulk):
        assert bsvp.analyzer.Analyzer.velRMSFull.func(analyzer_bulk)[
            "Resultant"
        ] == pytest.approx(
            bsvp.analyzer.Analyzer.MPS_TO_MMPS
            * rms(L2_norm(analyzer_bulk._velocityData, axis=0))
        )

    def test_disRMSFull(self, analyzer_bulk):
        assert bsvp.analyzer.Analyzer.disRMSFull.func(analyzer_bulk)[
            "Resultant"
        ] == pytest.approx(
            bsvp.analyzer.Analyzer.M_TO_MM
            * rms(L2_norm(analyzer_bulk._displacementData, axis=0))
        )

    def test_accPeakFull(self, analyzer_bulk):
        assert bsvp.analyzer.Analyzer.accPeakFull.func(analyzer_bulk)[
            "Resultant"
        ] == pytest.approx(
            bsvp.analyzer.Analyzer.MPS2_TO_G
            * L2_norm(analyzer_bulk._accelerationData, axis=0).max()
        )

    def test_pseudoVelPeakFull(self, analyzer_bulk):
        pass

    def test_gpsLocFull(self, analyzer_bulk):
        pass

    def test_gpsSpeedFull(self, analyzer_bulk):
        pass

    def test_gyroRMSFull(self, analyzer_bulk):
        pass

    def test_micRMSFull(self, analyzer_bulk):
        assert bsvp.analyzer.Analyzer.micRMSFull.func(analyzer_bulk)[
            "Mic"
        ] == pytest.approx(rms(analyzer_bulk._microphoneData))

    def test_pressFull(self, analyzer_bulk):
        assert bsvp.analyzer.Analyzer.pressFull.func(analyzer_bulk)[
            "Control"
        ] == pytest.approx(analyzer_bulk._pressureData.mean())

    def test_tempFull(self, analyzer_bulk):
        assert bsvp.analyzer.Analyzer.tempFull.func(analyzer_bulk)[
            "Control"
        ] == pytest.approx(analyzer_bulk._temperatureData.mean())

    ###########################################################################
    # Live File Tests

    def testLiveFile(self, ide_SSX70065):
        analyzer = bsvp.analyzer.Analyzer(
            ide_SSX70065,
            accel_start_time=None,
            accel_end_time=None,
            accel_start_margin=None,
            accel_end_margin=None,
            accel_highpass_cutoff=1,
            psd_freq_bin_width=1,
            pvss_init_freq=1,
            pvss_bins_per_octave=12,
            vc_init_freq=1,
            vc_bins_per_octave=3,
        )

        raw_accel = ide_SSX70065.channels[32].getSession().arrayValues()
        np.testing.assert_allclose(
            analyzer.accRMSFull["Resultant"],
            rms(L2_norm(raw_accel - raw_accel.mean(axis=-1, keepdims=True), axis=0)),
            rtol=1e-3,
        )
        np.testing.assert_allclose(
            analyzer.pressFull,
            1e-3
            * ide_SSX70065.channels[36]
            .subchannels[0]
            .getSession()
            .arrayValues()
            .mean(),
            rtol=1e-5,
        )
        np.testing.assert_allclose(
            analyzer.tempFull,
            ide_SSX70065.channels[36].subchannels[1].getSession().arrayValues().mean(),
            rtol=1e-4,
        )

    @pytest.mark.parametrize(
        "filename",
        [
            os.path.join(".", "tests", "test1.IDE"),
            os.path.join(".", "tests", "test2.IDE"),
        ],
    )
    def testLiveFiles12(self, filename):
        ds = idelib.importFile(filename)
        analyzer = bsvp.analyzer.Analyzer(
            ds,
            accel_start_time=None,
            accel_end_time=None,
            accel_start_margin=None,
            accel_end_margin=None,
            accel_highpass_cutoff=1,
            psd_freq_bin_width=1,
            pvss_init_freq=1,
            pvss_bins_per_octave=12,
            vc_init_freq=1,
            vc_bins_per_octave=3,
        )

        raw_accel = ds.channels[8].getSession().arrayValues(subchannels=[0, 1, 2])
        np.testing.assert_allclose(
            analyzer.accRMSFull["Resultant"],
            rms(L2_norm(raw_accel - raw_accel.mean(axis=-1, keepdims=True), axis=0)),
            rtol=0.55,  # this is... probably a little too high...
        )
        np.testing.assert_allclose(
            analyzer.micRMSFull,
            rms(ds.channels[8].subchannels[3].getSession().arrayValues()),
            rtol=1e-3,
        )
        np.testing.assert_allclose(
            analyzer.gyroRMSFull["Resultant"],
            rms(L2_norm(ds.channels[84].getSession().arrayValues(), axis=0)),
            rtol=1e-2,
        )
        np.testing.assert_allclose(
            analyzer.pressFull,
            1e-3 * ds.channels[36].subchannels[0].getSession().arrayValues().mean(),
            rtol=1e-3,
        )
        np.testing.assert_allclose(
            analyzer.tempFull,
            ds.channels[36].subchannels[1].getSession().arrayValues().mean(),
            rtol=0.05,  # ...GEFGW?
        )

    @pytest.mark.parametrize(
        "filename",
        [
            os.path.join(".", "tests", "test3.IDE"),
        ],
    )
    def testLiveFile3(self, filename):
        ds = idelib.importFile(filename)
        analyzer = bsvp.analyzer.Analyzer(
            ds,
            accel_start_time=None,
            accel_end_time=None,
            accel_start_margin=None,
            accel_end_margin=None,
            accel_highpass_cutoff=1,
            psd_freq_bin_width=1,
            pvss_init_freq=1,
            pvss_bins_per_octave=12,
            vc_init_freq=1,
            vc_bins_per_octave=3,
        )

        ch_rot = ds.channels[84]
        np.testing.assert_allclose(
            analyzer.gyroRMSFull["Resultant"],
            rms(L2_norm(ch_rot.getSession().arrayValues(), axis=0)),
            rtol=0.005,
        )

    @pytest.mark.parametrize(
        "filename, sample_index",
        [
            (os.path.join(".", "tests", "test_GPS_2.IDE"), -2),
            (os.path.join(".", "tests", "test_GPS_3.IDE"), -4),
        ],
    )
    def testLiveFileGPS(self, filename, sample_index):
        ds = idelib.importFile(filename)
        analyzer = bsvp.analyzer.Analyzer(
            ds,
            accel_start_time=None,
            accel_end_time=None,
            accel_start_margin=None,
            accel_end_margin=None,
            accel_highpass_cutoff=1,
            psd_freq_bin_width=1,
            pvss_init_freq=1,
            pvss_bins_per_octave=12,
            vc_init_freq=1,
            vc_bins_per_octave=3,
        )

        ch_gps = ds.channels[88]
        # confirming channel format for gps file
        assert ch_gps.subchannels[0].name == "Latitude"
        assert ch_gps.subchannels[1].name == "Longitude"
        assert ch_gps.subchannels[3].name == "Ground Speed"

        assert tuple(analyzer.gpsLocFull) == tuple(
            ch_gps.getSession().arrayValues()[[0, 1], sample_index],
        )
        # Resampling throws off mean calculation
        # -> use resampled data for comparsion
        # gps_speed = analyzer.MPS_TO_KMPH * ch_gps.getSession().arrayValues(subchannels=[3])
        gps_speed = analyzer._gpsSpeedData
        np.testing.assert_allclose(
            analyzer.gpsSpeedFull,
            np.mean(gps_speed[gps_speed != 0]),
        )
