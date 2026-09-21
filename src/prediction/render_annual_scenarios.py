"""Render annualized 2024–2030 scenario overlays from the existing 2030 model output.

These are not independently retrained annual forecasts.  They distribute the
existing cumulative 2030 transition probability across years using a constant
annual hazard: p(t) = 1 - (1 - p2030) ** (t / 7).
"""

from pathlib import Path

import numpy as np
import rasterio
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "outputs" / "predictions" / "urban_growth_probability_2030.tif"
DESTINATION = ROOT / "frontend" / "public" / "maps"
ENDPOINT_BANDS = (0.08, 0.16, 0.28, 0.42)
COLORS = ((255, 231, 143, 105), (246, 189, 96, 150), (232, 111, 67, 195), (154, 34, 37, 235))


def annual_probability(endpoint_probability: np.ndarray, elapsed_years: int) -> np.ndarray:
    return 1 - np.power(1 - endpoint_probability, elapsed_years / 7)


def to_overlay(probability: np.ndarray, thresholds: tuple[float, ...]) -> np.ndarray:
    overlay = np.zeros((*probability.shape, 4), dtype=np.uint8)
    valid = np.isfinite(probability)
    edges = (*thresholds, float("inf"))
    lower = 0.0
    for upper, color in zip(edges, COLORS):
        overlay[valid & (probability >= lower) & (probability < upper)] = color
        lower = upper
    return overlay


def main() -> None:
    with rasterio.open(SOURCE) as dataset:
        endpoint = dataset.read(1)

    DESTINATION.mkdir(parents=True, exist_ok=True)
    for year in range(2024, 2031):
        elapsed = year - 2023
        annual = annual_probability(endpoint, elapsed)
        thresholds = tuple(annual_probability(np.array(value), elapsed).item() for value in ENDPOINT_BANDS)
        Image.fromarray(to_overlay(annual, thresholds), "RGBA").save(DESTINATION / f"layer-{year}.png")


if __name__ == "__main__":
    main()
