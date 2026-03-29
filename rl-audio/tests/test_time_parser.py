from rlaudio.core.time_parser import format_seconds, parse_time_input


def test_parse_mm_ss():
    assert parse_time_input("01:30") == 90.0


def test_parse_mm_ss_ms():
    assert parse_time_input("02:15:500") == 135.5


def test_format_seconds():
    assert format_seconds(135.5) == "02:15:500"
