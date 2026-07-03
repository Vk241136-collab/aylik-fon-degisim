from dataclasses import dataclass

from rapidfuzz import fuzz

from app.core.normalization import normalize_code, normalize_text
from app.domain.models import PortfolioAsset


@dataclass(slots=True)
class MatchResult:
    previous: PortfolioAsset | None
    current: PortfolioAsset | None
    confidence: int
    method: str


def asset_identity(asset: PortfolioAsset) -> str:
    return (
        normalize_code(asset.isin)
        or normalize_code(asset.ticker)
        or normalize_code(asset.asset_code)
        or normalize_code(asset.contract_code)
        or normalize_text(asset.asset_name)
    )


def match_assets(previous: list[PortfolioAsset], current: list[PortfolioAsset]) -> list[MatchResult]:
    unmatched_current = current.copy()
    results: list[MatchResult] = []

    for prev in previous:
        match, confidence, method = _find_best(prev, unmatched_current)
        if match:
            unmatched_current.remove(match)
            results.append(MatchResult(prev, match, confidence, method))
        else:
            results.append(MatchResult(prev, None, 0, "unmatched_previous"))

    for cur in unmatched_current:
        results.append(MatchResult(None, cur, 0, "unmatched_current"))

    return results


def _find_best(prev: PortfolioAsset, candidates: list[PortfolioAsset]) -> tuple[PortfolioAsset | None, int, str]:
    exact_rules = [
        ("isin", prev.isin, lambda item: item.isin),
        ("ticker", prev.ticker, lambda item: item.ticker),
        ("asset_code", prev.asset_code, lambda item: item.asset_code),
        ("contract_code", prev.contract_code, lambda item: item.contract_code),
    ]
    for method, value, getter in exact_rules:
        needle = normalize_code(value)
        if not needle:
            continue
        for candidate in candidates:
            if needle == normalize_code(getter(candidate)):
                return candidate, 100, method

    prev_issuer = normalize_text(prev.issuer_name)
    issuer_key = f"{prev_issuer}|{normalize_text(prev.asset_type)}"
    if prev_issuer:
        for candidate in candidates:
            candidate_issuer = normalize_text(candidate.issuer_name)
            candidate_key = f"{candidate_issuer}|{normalize_text(candidate.asset_type)}"
            if candidate_issuer and issuer_key == candidate_key:
                return candidate, 88, "issuer_asset_type"

    prev_name = normalize_text(prev.asset_name)
    best: PortfolioAsset | None = None
    best_score = 0
    for candidate in candidates:
        if _has_conflicting_strong_identifier(prev, candidate):
            continue
        score = fuzz.token_sort_ratio(prev_name, normalize_text(candidate.asset_name))
        if score > best_score:
            best = candidate
            best_score = score
    if best and best_score >= 50:
        return best, int(best_score), "fuzzy_asset_name"
    return None, 0, "no_match"


def _has_conflicting_strong_identifier(prev: PortfolioAsset, candidate: PortfolioAsset) -> bool:
    for left, right in (
        (prev.isin, candidate.isin),
        (prev.ticker, candidate.ticker),
        (prev.asset_code, candidate.asset_code),
        (prev.contract_code, candidate.contract_code),
    ):
        left_code = normalize_code(left)
        right_code = normalize_code(right)
        if left_code and right_code and left_code != right_code:
            return True
    return False
