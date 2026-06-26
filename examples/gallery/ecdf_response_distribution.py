"""Gallery workflow: ECDF response distributions from a DataFrame recipe."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import figstudio


GALLERY_SPEC = Path(__file__).with_suffix(".figstudio.json")


def build_dataset() -> pd.DataFrame:
    measurements = {
        "Control": [82, 91, 97, 104, 113, 119, 127, 136, 148, 156],
        "Treatment": [68, 74, 79, 88, 93, 101, 109, 116, 123, 131],
        "Recovery": [76, 84, 90, 96, 106, 112, 121, 129, 138, 145],
    }
    rows = []
    for cohort, latencies in measurements.items():
        for sample_index, latency_ms in enumerate(latencies, start=1):
            rows.append(
                {
                    "cohort": cohort,
                    "sample_id": f"{cohort[:3].lower()}-{sample_index:02d}",
                    "latency_ms": latency_ms,
                }
            )
    return pd.DataFrame(rows)


df = build_dataset()


if __name__ == "__main__":
    print(f"Companion spec: {GALLERY_SPEC}")
    figstudio.open(locals(), script_path=__file__, block_id="ecdf_response_distribution")


# figstudio:start ecdf_response_distribution
# figstudio:end ecdf_response_distribution
