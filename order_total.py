from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from numbers import Number


def _as_decimal(value: object, name: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (Number, str, Decimal)):
        raise ValueError(f"{name} must be a finite number")
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{name} must be a finite number") from None
    if not amount.is_finite():
        raise ValueError(f"{name} must be a finite number")
    return amount


def calculate_order_total(subtotal: object, discount_percent: object = 0) -> float:
    """Return a discounted order total rounded to cents."""
    subtotal_value = _as_decimal(subtotal, "subtotal")
    discount_value = _as_decimal(discount_percent, "discount_percent")

    if subtotal_value < 0:
        raise ValueError("subtotal cannot be negative")
    if not Decimal("0") <= discount_value <= Decimal("100"):
        raise ValueError("discount_percent must be between 0 and 100")

    total = subtotal_value * (Decimal("1") - discount_value / Decimal("100"))
    return float(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


if __name__ == "__main__":
    total = calculate_order_total(50, 10)
    print(f"Order total: ${total:.2f}")
