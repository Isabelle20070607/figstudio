"""Gallery workflow: grouped category violins from a DataFrame recipe."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import figstudio


GALLERY_SPEC = Path(__file__).with_suffix(".figstudio.json")


def build_dataset() -> pd.DataFrame:
    measurements = {
        ("Baseline", "WT"): [0.91, 0.98, 1.04, 0.96, 1.02, 1.07, 1.12, 0.94],
        ("Baseline", "Mutant"): [0.74, 0.81, 0.86, 0.79, 0.84, 0.9, 0.88, 0.77],
        ("Stim A", "WT"): [1.24, 1.31, 1.36, 1.29, 1.42, 1.47, 1.33, 1.38],
        ("Stim A", "Mutant"): [1.03, 1.08, 1.14, 1.1, 1.18, 1.21, 1.06, 1.16],
        ("Stim B", "WT"): [1.53, 1.61, 1.68, 1.57, 1.72, 1.77, 1.63, 1.7],
        ("Stim B", "Mutant"): [1.28, 1.34, 1.41, 1.37, 1.45, 1.49, 1.32, 1.43],
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
    figstudio.open(locals(), script_path=__file__, block_id="category_violin_response")


# figstudio:start category_violin_response
# figstudio:end category_violin_response
