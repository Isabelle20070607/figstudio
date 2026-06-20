"""Gallery workflow: spanned GridSpec layout with selected mapping panels."""

from __future__ import annotations

from pathlib import Path

import numpy as np

import figstudio


GALLERY_SPEC = Path(__file__).with_suffix(".figstudio.json")


def build_data(seed: int = 21) -> tuple[np.ndarray, dict[str, np.ndarray], np.ndarray]:
    rng = np.random.default_rng(seed)
    time = np.linspace(0, 60, 180)
    control = np.sin(time / 5.0) + 0.18 * np.sin(time / 1.7) + rng.normal(0.0, 0.08, time.size)
    treated = 0.55 * np.sin(time / 5.0 + 0.7) + rng.normal(0.0, 0.07, time.size)

    frequency = np.linspace(1.0, 40.0, 48)
    center = 12.0 + 4.0 * np.sin(time / 18.0)
    spectral_power = np.exp(-((frequency[:, None] - center[None, :]) ** 2) / 35.0)
    spectral_power += 0.05 * rng.random(spectral_power.shape)

    return time, {"control": control, "treated": treated}, spectral_power


time, signal_map, spectral_power = build_data()


if __name__ == "__main__":
    print(f"Companion spec: {GALLERY_SPEC}")
    figstudio.open(locals(), script_path=__file__, block_id="spanned_layout_signal_map")


# figstudio:start spanned_layout_signal_map
# figstudio:end spanned_layout_signal_map
