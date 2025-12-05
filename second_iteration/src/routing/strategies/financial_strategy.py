"""Strategy tuned for financial datasets."""

from __future__ import annotations

import re

from ..base_strategy import BaseStrategy

try:  # pragma: no cover - script fallback
    from ...normalization.cleaner import Cleaner
except ImportError:  # pragma: no cover
    from normalization.cleaner import Cleaner

_FINANCE_TOKENS = (
    "amount",
    "revenue",
    "fine",
    "fee",
    "tax",
    "payment",
    "cost",
    "price",
    "balance",
)


class FinancialStrategy(BaseStrategy):
    """Adds finance specific annotations."""

    def apply(self, record: dict[str, object]) -> dict[str, object]:
        cleaned = Cleaner.clean_record(record or {})
        totals = []
        for key, value in cleaned.items():
            if not isinstance(key, str):
                continue
            if not any(token in key for token in _FINANCE_TOKENS):
                continue
            number = _to_number(value)
            if number is not None:
                totals.append(number)

        cleaned["financial_total"] = sum(totals) if totals else None
        cleaned["has_financial_red_flag"] = bool(
            cleaned.get("financial_total") and cleaned["financial_total"] > 1_000_000
        )
        cleaned["_strategy"] = self.name
        return cleaned


def _to_number(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        normalized = re.sub(r"[,$]", "", value)
        try:
            return float(normalized)
        except ValueError:
            return None
    return None
