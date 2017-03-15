from slither.data_utils import DataDisplay
from nose.tools import assert_equal


def test_display_time_with_zero_padding():
    data_display = DataDisplay()
    assert_equal(data_display.display_time(61), "00:01:01 h")
    assert_equal(data_display.display_time(3601), "01:00:01 h")