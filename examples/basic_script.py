"""Minimal FigStudio script workflow."""

import numpy as np
import pandas as pd

import figstudio


df = pd.DataFrame(
    {
        "time": np.linspace(0, 10, 100),
        "signal": np.sin(np.linspace(0, 10, 100)),
    }
)

figstudio.open(locals(), script_path=__file__, block_id="main")

# figstudio:start main
# figstudio:end main
