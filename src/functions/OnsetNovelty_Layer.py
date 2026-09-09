"""
Onset novelty/onset-strength visualization layer.
Visualizes the onset strength envelope computed from audio.
"""

import numpy as np
from matplotlib.axes import Axes
from typing import Dict, Any, List, Tuple, Optional

# Import Layer base class and shape primitives
from .visualization_system import Layer
from .shapes import Curve


class OnsetNovelty(Curve):
    # =========
    # INITIALIZATION AND CONFIGURATION
    def __init__(self, name: str = "Onset Novelty",
                 color: str = "darkorange",
                 line_width: float = 0.5,
                 alpha: float = 1.0):
        super().__init__(name, color=color, line_width=line_width, alpha=alpha,
                          label="Onset Novelty", secondary_axis=False, svg_class="onset-novelty")
    # =========

    def load_data(self, audio_path: str, print_output: bool = False, **kwargs) -> bool:
        # ========================================================
        # LOAD AUDIO & COMPUTE ONSET NOVELTY
        import librosa
        from pathlib import Path
        try:
            audio, sr = librosa.load(audio_path, sr=None, mono=False)
            filename = Path(audio_path).stem

            if audio.ndim == 2:
                audio = np.mean(audio, axis=0)

            # Compute onset strength (novelty) using librosa
            hoplen = 512
            onset_strength = librosa.onset.onset_strength(y=audio, sr=sr, hop_length=hoplen)
            
            # Convert frame indices to time
            times = librosa.frames_to_time(np.arange(len(onset_strength)), sr=sr, hop_length=hoplen)

            self._data = {
                "onset_strength": onset_strength,
                "times": times,
                "sr": sr,
                "filename": filename,
                "audio": audio
            }
            if print_output:
                print(f"✓ OnsetNovelty: Loaded {filename}, {len(onset_strength)} frames")
            return True
        # LOAD AUDIO & COMPUTE ONSET NOVELTY
        # ========================================================

        except Exception as e:
            print(f"✗ OnsetNovelty error: {e}")
            return False

    def _get_xy(self, shared_data: Dict[str, Any]) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        if self._data is None:
            return None
        return self._data["times"], self._data["onset_strength"]

    def draw(self, ax: Axes, shared_data: Dict[str, Any]) -> Tuple[List, List]:
        # ========================================================
        # PAINT ONSET NOVELTY
        if self._data is None:
            print("✗ OnsetNovelty: No data loaded")
            return [], []

        lines, labels = super().draw(ax, shared_data)

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Onset Strength")
        ax.set_title(f"Onset Novelty: {self._data['filename']}")
        
        # Set y-limits: onset strength is always non-negative, so start from 0
        onset_max = float(np.max(self._data["onset_strength"]))
        y_upper = onset_max * 1.15 if onset_max > 0 else 1.0  # Add 15% padding above max
        ax.set_ylim(0.0, y_upper)
        
        import matplotlib.ticker as ticker
        ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))

        shared_data.update(self._data)
        # PAINT ONSET NOVELTY
        # ========================================================

        return lines, labels
