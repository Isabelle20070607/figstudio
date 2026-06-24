"""Gallery workflow: stacked categorical composition from a DataFrame recipe."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import figstudio


GALLERY_SPEC = Path(__file__).with_suffix(".figstudio.json")


def build_dataset() -> pd.DataFrame:
    stages = [
        ("intake", "Intake", {"Pass": 32, "Flagged": 7, "Reject": 3}),
        ("prep", "Prep", {"Pass": 29, "Flagged": 10, "Reject": 5}),
        ("analysis", "Analysis", {"Pass": 36, "Flagged": 8, "Reject": 2}),
        ("review", "Review", {"Pass": 41, "Flagged": 4, "Reject": 1}),
    ]
    statuses = ["Pass", "Flagged", "Reject"]

    rows = []
    for stage_key, stage_label, counts in stages:
        for status in statuses:
            for index in range(1, counts[status] + 1):
                rows.append(
                    {
                        "sample_id": f"{stage_key}-{status.lower()}-{index:03d}",
                        "stage": stage_label,
                        "qc_status": status,
                    }
                )
    return pd.DataFrame(rows)


df = build_dataset()


if __name__ == "__main__":
    print(f"Companion spec: {GALLERY_SPEC}")
    figstudio.open(locals(), script_path=__file__, block_id="stacked_bar_sample_composition")


# figstudio:start stacked_bar_sample_composition
# figstudio:end stacked_bar_sample_composition
