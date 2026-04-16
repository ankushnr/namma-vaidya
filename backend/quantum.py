import numpy as np
import random

# Risk band definitions — must match analysis.py
BANDS = {
    "Low":      {"range": (0, 34),  "ce": "Ce-1", "level": "L1", "grade": "G-Mild"},
    "Moderate": {"range": (35, 64), "ce": "Ce-2", "level": "L2", "grade": "G-Moderate"},
    "High":     {"range": (65, 98), "ce": "Ce-3", "level": "L3", "grade": "G-Critical"},
}

def _score_to_band(score: int) -> str:
    if score <= 34:
        return "Low"
    elif score <= 64:
        return "Moderate"
    else:
        return "High"

def _band_to_index(band: str) -> int:
    return {"Low": 0, "Moderate": 1, "High": 2}[band]

def _index_to_band(idx: int) -> str:
    return ["Low", "Moderate", "High"][idx]

def quantum_optimize(raw_score: int) -> dict:
    """
    Quantum-inspired optimization pass.

    Concept: We treat the three risk bands as quantum states |0>, |1>, |2>.
    We compute superposition amplitudes biased by how close the raw score
    is to each band's midpoint. Then we apply a simulated 'measurement'
    (weighted random selection) to collapse to the final band.

    This mimics QAOA-style optimization: instead of a hard if-else cutoff,
    we evaluate all possibilities with probability amplitudes, and select
    the most likely optimal state under uncertainty.
    """

    # Step 1: Compute distance of raw_score from each band's midpoint
    band_midpoints = {
        "Low":      17,   # midpoint of 0-34
        "Moderate": 49,   # midpoint of 35-64
        "High":     81,   # midpoint of 65-98
    }

    # Step 2: Compute amplitudes (inverse distance = closer band gets higher amplitude)
    # Add 1 to avoid division by zero if score lands exactly on a midpoint
    raw_amplitudes = {}
    for band, midpoint in band_midpoints.items():
        distance = abs(raw_score - midpoint) + 1
        raw_amplitudes[band] = 1.0 / distance

    # Step 3: Apply quantum interference — boost the band that classical scoring picked
    classical_band = _score_to_band(raw_score)
    raw_amplitudes[classical_band] *= 2.5  # constructive interference on primary state

    # Step 4: Normalise amplitudes to get probability distribution (Born rule)
    total = sum(raw_amplitudes.values())
    probabilities = {band: amp / total for band, amp in raw_amplitudes.items()}

    # Step 5: Simulated quantum measurement — weighted random collapse
    bands = list(probabilities.keys())
    weights = [probabilities[b] for b in bands]
    measured_band = random.choices(bands, weights=weights, k=1)[0]

    # Step 6: Compute a quantum confidence score (0-100)
    # Higher = measurement strongly favoured one state
    confidence = round(probabilities[measured_band] * 100, 1)

    return {
        "quantum_band":        measured_band,
        "quantum_ce":          BANDS[measured_band]["ce"],
        "quantum_level":       BANDS[measured_band]["level"],
        "quantum_grade":       BANDS[measured_band]["grade"],
        "quantum_confidence":  confidence,
        "classical_band":      classical_band,
        "probabilities": {
            "Low":      round(probabilities["Low"] * 100, 1),
            "Moderate": round(probabilities["Moderate"] * 100, 1),
            "High":     round(probabilities["High"] * 100, 1),
        }
    }