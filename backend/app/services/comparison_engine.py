from decimal import Decimal
from uuid import UUID

from app.core.decimal_utils import delta, estimate_unit_price, pct_change, to_ratio
from app.domain.enums import ChangeStatus
from app.domain.models import ComparisonAssetResult, PortfolioAsset
from app.services.matching import asset_identity, match_assets


class ComparisonEngine:
    def compare(self, previous: list[PortfolioAsset], current: list[PortfolioAsset]) -> list[ComparisonAssetResult]:
        results: list[ComparisonAssetResult] = []
        for match in match_assets(previous, current):
            prev = match.previous
            cur = match.current
            statuses = self._statuses(prev, cur, match.confidence)
            prev_price, cur_price, estimated = self._unit_prices(prev, cur)
            quantity_delta = delta(prev.quantity if prev else None, cur.quantity if cur else None)
            market_delta = delta(prev.market_value if prev else None, cur.market_value if cur else None)
            weight_delta = delta(prev.portfolio_weight if prev else None, cur.portfolio_weight if cur else None)

            transaction_effect = None
            price_effect = None
            if prev and cur and quantity_delta is not None and prev_price is not None and cur_price is not None:
                transaction_effect = quantity_delta * prev_price
                price_effect = cur.quantity * (cur_price - prev_price) if cur.quantity is not None else None

            asset = cur or prev
            assert asset is not None
            results.append(
                ComparisonAssetResult(
                    asset_key=asset_identity(asset),
                    asset_name=asset.asset_name,
                    asset_type=asset.asset_type,
                    previous_asset=prev,
                    current_asset=cur,
                    match_confidence=match.confidence,
                    match_method=match.method,
                    statuses=statuses,
                    quantity_delta=quantity_delta,
                    quantity_change_pct=pct_change(prev.quantity if prev else None, cur.quantity if cur else None),
                    market_value_delta=market_delta,
                    market_value_change_pct=pct_change(prev.market_value if prev else None, cur.market_value if cur else None),
                    weight_delta_pp=weight_delta,
                    weight_change_pct=pct_change(prev.portfolio_weight if prev else None, cur.portfolio_weight if cur else None),
                    transaction_effect=transaction_effect,
                    price_effect=price_effect,
                    unit_price_is_estimated=estimated,
                )
            )
        return results

    def _statuses(self, prev: PortfolioAsset | None, cur: PortfolioAsset | None, confidence: int) -> list[ChangeStatus]:
        if prev is None:
            return [ChangeStatus.NEW_POSITION]
        if cur is None:
            return [ChangeStatus.EXITED_POSITION]

        statuses: list[ChangeStatus] = []
        if confidence < 75:
            statuses.append(ChangeStatus.MATCH_REVIEW_REQUIRED)
        if prev.asset_type != cur.asset_type:
            statuses.append(ChangeStatus.RECLASSIFIED)
        if cur.portfolio_weight is not None and prev.portfolio_weight is not None:
            if cur.portfolio_weight > prev.portfolio_weight:
                statuses.append(ChangeStatus.WEIGHT_INCREASED)
            elif cur.portfolio_weight < prev.portfolio_weight:
                statuses.append(ChangeStatus.WEIGHT_DECREASED)
        if cur.quantity is not None and prev.quantity is not None:
            if cur.quantity > prev.quantity:
                statuses.append(ChangeStatus.QUANTITY_INCREASED)
            elif cur.quantity < prev.quantity:
                statuses.append(ChangeStatus.QUANTITY_DECREASED)
        return statuses or [ChangeStatus.UNCHANGED]

    def _unit_prices(self, prev: PortfolioAsset | None, cur: PortfolioAsset | None) -> tuple[Decimal | None, Decimal | None, bool]:
        estimated = False
        prev_price = prev.unit_price if prev else None
        cur_price = cur.unit_price if cur else None
        if prev and prev_price is None:
            prev_price = estimate_unit_price(prev.quantity, prev.market_value)
            estimated = estimated or prev_price is not None
        if cur and cur_price is None:
            cur_price = estimate_unit_price(cur.quantity, cur.market_value)
            estimated = estimated or cur_price is not None
        return prev_price, cur_price, estimated


def hhi(assets: list[PortfolioAsset]) -> Decimal:
    return sum((to_ratio(asset.portfolio_weight) ** 2 for asset in assets), Decimal("0"))
