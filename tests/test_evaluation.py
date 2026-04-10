"""Basic tests for the mango evaluation module."""

from mango.evaluation.utils.utils import edit_distance, parse_raw_output


def test_edit_distance_identical():
    assert edit_distance("hello", "hello") == 1.0


def test_edit_distance_completely_different():
    score = edit_distance("abc", "xyz")
    assert 0.0 <= score <= 1.0


def test_edit_distance_empty():
    assert edit_distance("", "") == 0


def test_parse_raw_output_valid_list():
    raw = [{"location_before": "A", "action": "north", "location_after": "B"}]
    result, error = parse_raw_output(raw)
    assert result is not None
    assert error is None


def test_parse_raw_output_valid_string():
    raw = "[{'location_before': 'A', 'action': 'north', 'location_after': 'B'}]"
    result, error = parse_raw_output(raw)
    assert result is not None
    assert error is None


def test_parse_raw_output_invalid():
    result, error = parse_raw_output("not valid output")
    assert result is None
    assert error is not None
