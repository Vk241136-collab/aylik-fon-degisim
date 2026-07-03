from decimal import Decimal
from uuid import uuid4

from app.domain.enums import ChangeStatus
from app.domain.models import PortfolioAsset
from app.services.comparison_engine import ComparisonEngine


def make_asset(report_id, code, quantity, price, weight):
    return PortfolioAsset(
        report_id=report_id,
        asset_type="Hisse senedi",
        asset_name=f"{code} A.Ş.",
        asset_code=code,
        ticker=code,
        quantity=Decimal(quantity),
        unit_price=Decimal(price),
        market_value=Decimal(quantity) * Decimal(price),
        portfolio_weight=Decimal(weight),
    )


def test_new_and_exited_positions_are_detected():
    previous_id = uuid4()
    current_id = uuid4()
    previous = [make_asset(previous_id, "ASELS", "10", "100", "5")]
    current = [make_asset(current_id, "THYAO", "10", "100", "5")]

    results = ComparisonEngine().compare(previous, current)

    assert any(ChangeStatus.EXITED_POSITION in result.statuses for result in results)
    assert any(ChangeStatus.NEW_POSITION in result.statuses for result in results)


def test_weight_increases_while_quantity_decreases():
    previous_id = uuid4()
    current_id = uuid4()
    previous = [make_asset(previous_id, "TUPRS", "100", "10", "10")]
    current = [make_asset(current_id, "TUPRS", "90", "20", "12")]

    result = ComparisonEngine().compare(previous, current)[0]

    assert ChangeStatus.QUANTITY_DECREASED in result.statuses
    assert ChangeStatus.WEIGHT_INCREASED in result.statuses
    assert result.quantity_delta == Decimal("-10")
    assert result.weight_delta_pp == Decimal("2")


def test_fuzzy_name_match_needs_review():
    previous_id = uuid4()
    current_id = uuid4()
    previous = [PortfolioAsset(report_id=previous_id, asset_type="Devlet tahvili", asset_name="TRT120328T12 Devlet Tahvili")]
    current = [PortfolioAsset(report_id=current_id, asset_type="Devlet tahvili", asset_name="TRT120328T12 Dev. Tahvili")]

    result = ComparisonEngine().compare(previous, current)[0]

    assert result.match_confidence >= 50
    assert result.match_method == "fuzzy_asset_name"
