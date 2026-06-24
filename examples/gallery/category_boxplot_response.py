"""Gallery workflow: grouped category boxplots from a DataFrame recipe."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import figstudio


GALLERY_SPEC = Path(__file__).with_suffix(".figstudio.json")


def build_dataset() -> pd.DataFrame:
    measurements = {
        ("Control", "WT"): [0.92, 1.01, 1.08, 0.97, 1.04, 1.12],
        ("Control", "Mutant"): [0.78, 0.84, 0.91, 0.88, 0.82, 0.86],
        ("Stim A", "WT"): [1.28, 1.35, 1.42, 1.31, 1.39, 1.47],
        ("Stim A", "Mutant"): [1.05, 1.12, 1.18, 1.09, 1.15, 1.21],
        ("Stim B", "WT"): [1.58, 1.66, 1.71, 1.61, 1.69, 1.75],
        ("Stim B", "Mutant"): [1.33, 1.41, 1.48, 1.37, 1.44, 1.51],
    }
    rows = []
    for (condition, genotype), values in measurements.items():
        for replicate, response in enumerate(values, start=1):
            rows.append(
                {
                    "condition": condition,
                    "genotype": genotype,
                    "replicate": replicate,
                    "response": response,
                }
            )
    return pd.DataFrame(rows)


df = build_dataset()


if __name__ == "__main__":
    print(f"Companion spec: {GALLERY_SPEC}")
    figstudio.open(locals(), script_path=__file__, block_id="category_boxplot_response")


# figstudio:start category_boxplot_response
# figstudio:end category_boxplot_response
