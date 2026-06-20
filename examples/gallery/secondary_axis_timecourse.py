"""Gallery workflow: primary signal with a secondary event-rate axis."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import figstudio


GALLERY_SPEC = Path(__file__).with_suffix(".figstudio.json")


def build_dataset(seed: int = 13) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    time = np.linspace(0, 60, 121)
    stimulus = (time >= 24) & (time <= 36)
    fluorescence = (
        1.0
        + 0.35 * np.sin(time / 6.0)
        + 0.75 * np.exp(-((time - 30.0) ** 2) / 90.0)
        + rng.normal(0.0, 0.035, size=time.size)
    )
    event_rate = (
        4.0
        + 1.2 * np.sin(time / 8.0 + 0.6)
        + 6.0 * np.exp(-((time - 30.0) ** 2) / 70.0)
        + rng.normal(0.0, 0.25, size=time.size)
    )
    event_rate = np.clip(event_rate, 0.5, None)

    return pd.DataFrame(
        {
            "time": time,
            "fluorescence": fluorescence,
            "event_rate": event_rate,
            "stimulus": stimulus,
        }
    )


df = build_dataset()


if __name__ == "__main__":
    print(f"Companion spec: {GALLERY_SPEC}")
    figstudio.open(locals(), script_path=__file__, block_id="secondary_axis_timecourse")


# figstudio:start secondary_axis_timecourse
# figstudio:end secondary_axis_timecourse
