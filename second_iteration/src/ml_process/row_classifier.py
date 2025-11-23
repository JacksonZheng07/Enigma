"""Gradient boosted row classifier that can persist its model."""

from __future__ import annotations

import base64
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence
import numpy as np
import xgboost as xgb

_FEATURE_KEYS = [
    "null_ratio",
    "empty_text_ratio",
    "numeric_zero_ratio",
    "short_text_ratio",
    "essential_missing_ratio",
]

_ESSENTIAL_FIELDS = {
    "dca_license_number",
    "license_number",
    "provider_record_id",
    "business_name",
    "canonical_legal_entity_name",
    "street_address",
    "address_city",
    "city",
    "address_state",
    "state",
    "zip_code",
    "latitude",
    "longitude",
    "contact_phone_number",
    "phone",
    "phone_number",
}

_DEFAULT_MEANS = {
    "null_ratio": 0.15,
    "empty_text_ratio": 0.05,
    "numeric_zero_ratio": 0.1,
    "short_text_ratio": 0.1,
    "essential_missing_ratio": 0.3,
}

_DEFAULT_SCALES = {
    "null_ratio": 0.15,
    "empty_text_ratio": 0.05,
    "numeric_zero_ratio": 0.08,
    "short_text_ratio": 0.05,
    "essential_missing_ratio": 0.2,
}

_HEURISTIC_BIAS = -1.0
_HEURISTIC_WEIGHTS = {
    "null_ratio": 3.0,
    "empty_text_ratio": 1.6,
    "numeric_zero_ratio": 1.2,
    "short_text_ratio": 1.3,
    "essential_missing_ratio": 4.0,
}


@dataclass
class RowDropClassifier:
    """Train a lightweight XGBoost model (with heuristic fallback) to drop rows."""

    threshold: float = 0.65
    feature_means: dict[str, float] = field(default_factory=lambda: dict(_DEFAULT_MEANS))
    feature_scales: dict[str, float] = field(default_factory=lambda: dict(_DEFAULT_SCALES))
    booster: object | None = field(default=None, init=False)
    model_type: str = field(default="heuristic", init=False)

    def fit(self, records: Sequence[dict[str, object]]) -> RowDropClassifier:
        """Fit the classifier against pseudo-labels derived from heuristics."""
        features = [self._compute_features(record) for record in records]
        if not features:
            self.feature_means = dict(_DEFAULT_MEANS)
            self.feature_scales = dict(_DEFAULT_SCALES)
            self.model_type = "heuristic"
            self.booster = None
            return self

        self._recompute_feature_stats(features)

        feature_matrix = self._to_matrix(features)
        labels = self._pseudo_labels(features)

        if xgb is not None and len(set(labels)) > 1:
            dtrain = xgb.DMatrix(feature_matrix, label=labels, feature_names=_FEATURE_KEYS)
            params = {
                "objective": "binary:logistic",
                "max_depth": 2,
                "eta": 0.3,
                "subsample": 0.8,
                "colsample_bytree": 1.0,
                "lambda": 1.0,
                "min_child_weight": 1,
                "verbosity": 0,
            }
            self.booster = xgb.train(params, dtrain, num_boost_round=25)
            self.model_type = "xgboost"
        else:
            self.booster = None
            self.model_type = "heuristic"
        return self

    def predict_proba(self, records: Sequence[dict[str, object]]) -> list[float]:
        """Return drop probabilities for each record."""
        features = [self._compute_features(record) for record in records]
        if not features:
            return []

        if self.model_type == "xgboost" and self.booster is not None and xgb is not None:
            matrix = self._to_matrix(features)
            dmatrix = xgb.DMatrix(matrix, feature_names=_FEATURE_KEYS)
            return list(map(float, self.booster.predict(dmatrix)))

        return [self._heuristic_probability(row) for row in features]

    def predict_drop(self, records: Sequence[dict[str, object]], auto_fit: bool = True) -> list[bool]:
        """Return boolean mask indicating whether each record should be dropped."""
        if auto_fit:
            self.fit(records)
        probabilities = self.predict_proba(records)
        return [prob >= self.threshold for prob in probabilities]

    def filter_records(
        self, records: Sequence[dict[str, object]], auto_fit: bool = True
    ) -> tuple[list[dict[str, object]], int]:
        """Return (kept_records, dropped_count) after applying the classifier."""
        drop_mask = self.predict_drop(records, auto_fit=auto_fit)
        kept = [record for record, drop in zip(records, drop_mask) if not drop]
        return kept, sum(drop_mask)

    def save(self, path: Path | str) -> None:
        """Persist the trained classifier to disk."""
        metadata = {
            "threshold": self.threshold,
            "feature_means": self.feature_means,
            "feature_scales": self.feature_scales,
            "model_type": self.model_type,
            "booster": None,
        }
        if self.model_type == "xgboost" and self.booster is not None and xgb is not None:
            raw = self.booster.save_raw()
            metadata["booster"] = base64.b64encode(raw).decode("ascii")

        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(metadata), encoding="utf-8")

    @classmethod
    def load(cls, path: Path | str) -> RowDropClassifier:
        """Load a persisted classifier."""
        metadata = json.loads(Path(path).read_text(encoding="utf-8"))
        classifier = cls(threshold=metadata["threshold"])
        classifier.feature_means = metadata["feature_means"]
        classifier.feature_scales = metadata["feature_scales"]
        classifier.model_type = metadata.get("model_type", "heuristic")

        booster_blob = metadata.get("booster")
        if booster_blob and classifier.model_type == "xgboost" and xgb is not None:
            classifier.booster = xgb.Booster()
            raw = base64.b64decode(booster_blob.encode("ascii"))
            try:
                classifier.booster.load_model(bytearray(raw))
            except TypeError: 
                temp = Path(path).with_suffix(".xgb.tmp")
                temp.write_bytes(raw)
                classifier.booster.load_model(str(temp))
                temp.unlink(missing_ok=True)
        else:
            classifier.booster = None
            classifier.model_type = "heuristic"
        return classifier

    def _recompute_feature_stats(self, features: list[dict[str, float]]) -> None:
        self.feature_means = {}
        self.feature_scales = {}
        for key in _FEATURE_KEYS:
            values = [row[key] for row in features]
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / max(len(values), 1)
            scale = math.sqrt(variance) or _DEFAULT_SCALES[key]
            self.feature_means[key] = mean
            self.feature_scales[key] = scale

    def _pseudo_labels(self, features: list[dict[str, float]]) -> list[int]:
        labels: list[int] = []
        for row in features:
            drop = (
                row["null_ratio"] > 0.45
                or row["empty_text_ratio"] > 0.35
                or (row["null_ratio"] > 0.25 and row["short_text_ratio"] > 0.2)
                or row["numeric_zero_ratio"] > 0.5
                or row["essential_missing_ratio"] > 0.4
                or (row["essential_missing_ratio"] > 0.25 and row["null_ratio"] > 0.2)
            )
            labels.append(1 if drop else 0)
        return labels

    def _to_matrix(self, features: list[dict[str, float]]) -> np.ndarray:
        data = [[row[key] for key in _FEATURE_KEYS] for row in features]
        return np.asarray(data, dtype=float)

    def _heuristic_probability(self, feature_row: dict[str, float]) -> float:
        z = _HEURISTIC_BIAS
        for feature, weight in _HEURISTIC_WEIGHTS.items():
            standardized = self._standardize(feature, feature_row[feature])
            z += weight * standardized
        return self._sigmoid(z)

    def _standardize(self, feature: str, value: float) -> float:
        mean = self.feature_means.get(feature, _DEFAULT_MEANS[feature])
        scale = self.feature_scales.get(feature, _DEFAULT_SCALES[feature])
        if not scale:
            scale = _DEFAULT_SCALES[feature]
        return (value - mean) / scale

    @staticmethod
    def _sigmoid(value: float) -> float:
        return 1.0 / (1.0 + math.exp(-value))

    def _compute_features(self, record: dict[str, object]) -> dict[str, float]:
        row = dict(record or {})
        total_fields = max(len(row), 1)

        null_like = 0
        empty_text = 0
        short_text = 0
        numeric_zero = 0
        essential_missing = 0

        for value in row.values():
            if value is None or (isinstance(value, float) and math.isnan(value)):
                null_like += 1
                continue

            if isinstance(value, str):
                text = value.strip()
                if not text:
                    null_like += 1
                    empty_text += 1
                    continue
                if len(text) <= 2:
                    short_text += 1
                continue

            if isinstance(value, (int, float)):
                if value == 0:
                    numeric_zero += 1

        for field in _ESSENTIAL_FIELDS:
            if not _has_value(row.get(field)):
                essential_missing += 1

        return {
            "null_ratio": null_like / total_fields,
            "empty_text_ratio": empty_text / total_fields,
            "numeric_zero_ratio": numeric_zero / total_fields,
            "short_text_ratio": short_text / total_fields,
            "essential_missing_ratio": essential_missing / max(len(_ESSENTIAL_FIELDS), 1),
        }


def _has_value(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, float) and math.isnan(value):
        return False
    return True
