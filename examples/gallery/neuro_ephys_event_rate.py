"""Gallery workflow: bundled neuro ephys event-rate timecourse recipe."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import figstudio


GALLERY_SPEC = Path(__file__).with_suffix(".figstudio.json")


def build_dataset(seed: int = 29) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    time = np.arange(0, 70, 10)
    conditions = {
        "Spontaneous": 3.6 + 0.25 * np.sin(time / 18.0),
        "Stimulus": 4.0 + 4.1 * np.exp(-((time - 30.0) ** 2) / 180.0),
        "Recovery": 3.8 + 1.4 * np.exp(-((time - 35.0) ** 2) / 260.0),
    }

    rows = []
    for condition, profile in conditions.items():
        for unit_index in range(1, 9):
            unit_shift = rng.normal(0.0, 0.22)
            for time_s, expected_rate in zip(time, profile):
                event_rate_hz = max(0.1, expected_rate + unit_shift + rng.normal(0.0, 0.28))
                rows.append(
                    {
                        "condition": condition,
                        "unit_id": f"{condition[:3].lower()}-{unit_index:02d}",
                        "time_s": int(time_s),
                        "event_rate_hz": float(event_rate_hz),
                    }
                )
    return pd.DataFrame(rows)


df = build_dataset()


if __name__ == "__main__":
    print(f"Companion spec: {GALLERY_SPEC}")
    figstudio.open(locals(), script_path=__file__, block_id="neuro_ephys_event_rate")


# figstudio:start neuro_ephys_event_rate
# figstudio:end neuro_ephys_event_rate
