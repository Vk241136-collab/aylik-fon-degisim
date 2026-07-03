from decimal import Decimal

from app.core.decimal_utils import parse_decimal


def test_parse_turkish_decimal_formats():
    assert parse_decimal("%3,45") == Decimal("3.45")
    assert parse_decimal("1.250.000,50") == Decimal("1250000.50")
    assert parse_decimal("1,250,000.50") == Decimal("1250000.50")
