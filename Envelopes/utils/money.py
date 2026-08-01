from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


CENTS_PER_DOLLAR = 100


def dollars_to_cents(amount: float | str | Decimal) -> int:
    """
    Convert a dollar amount into integer cents.

    Examples:
        12.34 -> 1234
        "12.34" -> 1234
        -5.50 -> -550
    """

    try:
        decimal_amount = Decimal(str(amount))
    except InvalidOperation as error:
        raise ValueError(
            f"Invalid money amount: {amount}"
        ) from error

    rounded_amount = decimal_amount.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    return int(
        rounded_amount * CENTS_PER_DOLLAR
    )


def cents_to_dollars(amount_cents: int) -> Decimal:
    """
    Convert integer cents into a Decimal dollar amount.

    Example:
        1234 -> Decimal("12.34")
    """

    return (
        Decimal(amount_cents)
        / Decimal(CENTS_PER_DOLLAR)
    )


def format_currency(amount_cents: int) -> str:
    """
    Format integer cents as US currency.

    Examples:
        125050 -> "$1,250.50"
        -8216 -> "-$82.16"
    """

    amount = cents_to_dollars(amount_cents)

    if amount < 0:
        return f"-${abs(amount):,.2f}"

    return f"${amount:,.2f}"