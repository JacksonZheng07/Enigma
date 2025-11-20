"""Strategy tuned for financial datasets."""

from __future__ import annotations

from ..base_strategy import BaseStrategy


class FinancialStrategy(BaseStrategy):
    """Adds finance specific annotations."""

    def apply(self, record: dict[str, object]) -> dict[str, object]:
        raise NotImplementedError("Implement financial enrichment")
