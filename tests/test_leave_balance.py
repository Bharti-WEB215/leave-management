import pytest

from leave_balance import validate_leave_request


def test_valid_leave_request_within_balance():
    assert validate_leave_request(10, 4) is True


@pytest.mark.parametrize(
    ("available_days", "requested_days", "error"),
    [
        pytest.param(10, 4, None, id="valid-request"),
        pytest.param(10, 10, None, id="request-uses-full-balance"),
        pytest.param(2, 3, "exceeds", id="insufficient-balance"),
        pytest.param(10, 0, "greater than zero", id="zero-days"),
        pytest.param(10, -1, "greater than zero", id="negative-days"),
        pytest.param(-1, 1, "cannot be negative", id="negative-balance"),
        pytest.param(5.5, 2, "whole numbers", id="fractional-balance"),
        pytest.param(5, 1.5, "whole numbers", id="fractional-request"),
        pytest.param(True, 1, "whole numbers", id="boolean-balance"),
    ],
)
def test_leave_request_validation(available_days, requested_days, error):
    if error is None:
        assert validate_leave_request(available_days, requested_days) is True
    else:
        with pytest.raises(ValueError, match=error):
            validate_leave_request(available_days, requested_days)
