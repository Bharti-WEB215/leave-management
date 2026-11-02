import pytest

from leave_balance import validate_leave_request


def test_valid_leave_request_within_balance():
    assert validate_leave_request(10, 4) is True


@pytest.mark.parametrize(
    ("available_days", "requested_days"),
    [
        (0, 1),
        (5, 0),
        (5, -1),
        (-1, 1),
        (5, 6),
        (5.5, 2),
    ],
)
def test_invalid_leave_requests_raise(available_days, requested_days):
    with pytest.raises(ValueError):
        validate_leave_request(available_days, requested_days)
