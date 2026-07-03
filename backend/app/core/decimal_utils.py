from decimal import Decimal, InvalidOperation
import re


DECIMAL_ZERO = Decimal("0")


def parse_decimal(value: object) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    text = str(value).strip()
    if not text or text in {"-", "—", "nan", "None"}:
        return None

    text = text.replace("%", "").replace(" ", "")
    text = re.sub(r"[^\d,.\-]", "", text)
    if not text:
        return None

    last_comma = text.rfind(",")
    last_dot = text.rfind(".")
    if last_comma > last_dot:
        normalized = text.replace(".", "").replace(",", ".")
    elif last_dot > last_comma:
        normalized = text.replace(",", "")
    else:
        normalized = text.replace(",", ".")

    try:
        return Decimal(normalized)
    except InvalidOperation:
        return None


def pct_change(previous: Decimal | None, current: Decimal | None) -> Decimal | None:
    if previous is None or current is None or previous == DECIMAL_ZERO:
        return None
    return ((current - previous) / previous) * Decimal("100")


def delta(previous: Decimal | None, current: Decimal | None) -> Decimal | None:
    if previous is None or current is None:
        return None
    return current - previous


def estimate_unit_price(quantity: Decimal | None, market_value: Decimal | None) -> Decimal | None:
    if not quantity or quantity == DECIMAL_ZERO or market_value is None:
        return None
    return market_value / quantity


def to_ratio(weight_percent: Decimal | None) -> Decimal:
    if weight_percent is None:
        return DECIMAL_ZERO
    return weight_percent / Decimal("100")
