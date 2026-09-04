"""Explainable landslide risk scoring for the LandGuard demonstration system."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RiskResult:
    score: float
    level: str
    color: str
    reasons: list[str]


def _band(value: float, low: float, high: float) -> float:
    return float(np.clip((value - low) / (high - low), 0.0, 1.0))


def calculate_risk(row: pd.Series) -> RiskResult:
    """Calculate a 0-100 score from sensor and environmental indicators."""
    rainfall = _band(float(row["rainfall_24h_mm"]), 20, 180)
    soil_moisture = _band(float(row["soil_moisture_pct"]), 35, 95)
    slope = _band(float(row["slope_deg"]), 15, 45)
    displacement = _band(float(row["displacement_mm"]), 2, 30)
    seismic = _band(float(row["seismic_activity"]), 0.05, 0.8)

    score = round(100 * (0.30 * rainfall + 0.25 * soil_moisture + 0.20 * slope + 0.20 * displacement + 0.05 * seismic), 1)
    reasons: list[str] = []
    if rainfall >= 0.65:
        reasons.append("Heavy 24-hour rainfall")
    if soil_moisture >= 0.70:
        reasons.append("Soil moisture is near saturation")
    if slope >= 0.65:
        reasons.append("Steep terrain increases susceptibility")
    if displacement >= 0.45:
        reasons.append("Ground displacement is accelerating")
    if seismic >= 0.55:
        reasons.append("Elevated micro-seismic activity")
    if not reasons:
        reasons.append("Indicators remain within baseline range")

    if score >= 75:
        level, color = "CRITICAL", "#dc2626"
    elif score >= 50:
        level, color = "HIGH", "#ea580c"
    elif score >= 25:
        level, color = "MODERATE", "#ca8a04"
    else:
        level, color = "LOW", "#15803d"
    return RiskResult(score, level, color, reasons)


def score_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    results = data.apply(calculate_risk, axis=1)
    scored = data.copy()
    scored["risk_score"] = [result.score for result in results]
    scored["risk_level"] = [result.level for result in results]
    scored["risk_color"] = [result.color for result in results]
    scored["risk_reason"] = ["; ".join(result.reasons) for result in results]
    return scored
