"""Gallery workflow: DataFrame recipe facets for a dose-response panel."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import figstudio


GALLERY_SPEC = Path(__file__).with_suffix(".figstudio.json")


def build_dataset(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    timepoints = np.arange(0, 7)
    conditions = [
        ("control", "Control", 0.0),
        ("low_dose", "Low dose", 0.45),
        ("high_dose", "High dose", 0.9),
    ]

    rows = []
    for condition, label, effect in conditions:
        for replicate in range(1, 11):
            replicate_shift = rng.normal(0.0, 0.04)
            for time in timepoints:
                response = (
                    1.0
                    + effect * (1.0 - np.exp(-time / 2.2))
                    + 0.04 * time
                    + replicate_shift
                    + rng.normal(0.0, 0.05)
                )
                rows.append(
                    {
                        "condition": condition,
                        "condition_label": label,
                        "replicate": f"r{replicate:02d}",
                        "time": int(time),
                        "response": response,
                    }
                )
    return pd.DataFrame(rows)


df = build_dataset()


if __name__ == "__main__":
    print(f"Companion spec: {GALLERY_SPEC}")
    figstudio.open(locals(), script_path=__file__, block_id="faceted_dose_response")


# figstudio:start faceted_dose_response
# figstudio:end faceted_dose_response
