import pytest

from order_total import calculate_order_total


def test_normal_order_total_after_discount():
    assert calculate_order_total(100, 15) == 85.0


def test_zero_subtotal_returns_zero():
    assert calculate_order_total(0, 20) == 0.0


@pytest.mark.parametrize(
    ("subtotal", "discount"),
    [
        (-0.01, 0),
        (10, -1),
        (10, 100.01),
        ("not-a-number", 10),
        (float("nan"), 10),
    ],
)
def test_invalid_order_total_inputs_raise(subtotal, discount):
    with pytest.raises(ValueError):
        calculate_order_total(subtotal, discount)


@pytest.mark.parametrize(
    ("discount", "expected"),
    [
        (0, 100.0),
        (100, 0.0),
    ],
)
def test_discount_boundaries(discount, expected):
    assert calculate_order_total(100, discount) == expected


def test_total_rounds_to_cents():
    assert calculate_order_total(12.345, 0) == 12.35
