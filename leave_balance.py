def validate_leave_request(available_days: int, requested_days: int) -> bool:
    if (
        isinstance(available_days, bool)
        or isinstance(requested_days, bool)
        or not isinstance(available_days, int)
        or not isinstance(requested_days, int)
    ):
        raise ValueError("Leave balances must be whole numbers")
    if available_days < 0:
        raise ValueError("Available leave cannot be negative")
    if requested_days <= 0:
        raise ValueError("Requested leave must be greater than zero")
    if requested_days > available_days:
        raise ValueError("Requested leave exceeds the available balance")
    return True
