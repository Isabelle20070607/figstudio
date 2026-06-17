"""Synthetic DataFrame session for FigStudio general statistics recipes."""

import numpy as np
import pandas as pd

import figstudio


rng = np.random.default_rng(7)
subjects = [f"s{index:02d}" for index in range(1, 13)]
conditions = ["baseline", "treatment"]
timepoints = np.arange(6)

rows = []
for subject in subjects:
    subject_shift = rng.normal(0.0, 0.25)
    for condition_index, condition in enumerate(conditions):
        treatment_effect = 0.55 * condition_index
        for time in timepoints:
            rows.append(
                {
                    "subject": subject,
                    "condition": condition,
                    "time": int(time),
                    "signal": (
                        1.5
                        + 0.35 * time
                        + treatment_effect
                        + subject_shift
                        + rng.normal(0.0, 0.18)
                    ),
                    "endpoint": 1.0 + treatment_effect + subject_shift + rng.normal(0.0, 0.22),
                }
            )

df = pd.DataFrame(rows)

# Recipe ideas in the editor:
# - mean_sem_line: x=time, y=signal, group=condition
# - grouped_points: x=condition, y=endpoint
# - paired_before_after: x=condition, y=endpoint, subject=subject
figstudio.open(locals(), script_path=__file__, block_id="general_stats")

# figstudio:start general_stats
# figstudio:end general_stats
