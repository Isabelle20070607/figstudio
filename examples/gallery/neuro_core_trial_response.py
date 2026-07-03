"""Gallery workflow: bundled neuro core trial-response timecourse recipe."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import figstudio


GALLERY_SPEC = Path(__file__).with_suffix(".figstudio.json")


def build_dataset(seed: int = 43) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    time = np.arange(-100, 450, 50)
    profiles = {
        "Baseline": 0.08 * np.sin(time / 85.0),
        "Stimulus A": 1.35 * np.exp(-((time - 150.0) ** 2) / 16000.0),
        "Stimulus B": 1.95 * np.exp(-((time - 190.0) ** 2) / 19000.0),
    }

    rows = []
    for condition, profile in profiles.items():
        for trial_index in range(1, 13):
            trial_shift = rng.normal(0.0, 0.08)
            for time_ms, expected_response in zip(time, profile):
                response_z = expected_response + trial_shift + rng.normal(0.0, 0.12)
                rows.append(
                    {
                        "condition": condition,
                        "trial_id": f"{condition.lower().replace(' ', '-')}-{trial_index:02d}",
                        "time_ms": int(time_ms),
                        "response_z": float(response_z),
                    }
                )
    return pd.DataFrame(rows)


df = build_dataset()


if __name__ == "__main__":
    print(f"Companion spec: {GALLERY_SPEC}")
    figstudio.open(locals(), script_path=__file__, block_id="neuro_core_trial_response")


# figstudio:start neuro_core_trial_response
# figstudio:end neuro_core_trial_response
