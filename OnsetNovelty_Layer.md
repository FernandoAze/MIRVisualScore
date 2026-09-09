# OnsetNovelty Layer Implementation

## Overview
The `OnsetNovelty` class is a new `Curve` subclass that visualizes audio onset strength (novelty) as a line curve. It computes the onset-strength envelope using librosa and displays it alongside other visualization layers.

## Files Created

### `src/functions/OnsetNovelty_Layer.py`
A standalone module containing the `OnsetNovelty` class (93 lines total).

**Complete Implementation:**

```python
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
```

**Methods implemented:**

1. **`__init__(self, name: str = "Onset Novelty", color: str = "darkorange", line_width: float = 0.5, alpha: float = 1.0)`**
   - Initializes the layer with default parameters
   - Calls `super().__init__()` to configure the Curve base class
   - Sets `secondary_axis=False` (uses the main axis)
   - Sets `svg_class="onset-novelty"` for SVG rendering

2. **`load_data(self, audio_path: str, print_output: bool = False, **kwargs) -> bool`**
   - Loads audio file from `audio_path`
   - Handles stereo audio by averaging channels
   - Computes onset strength using `librosa.onset.onset_strength()` with `hop_length=512`
   - Converts frame indices to time values using `librosa.frames_to_time()`
   - Stores all data in `self._data` dictionary:
     - `"onset_strength"`: numpy array of onset strength values (always non-negative)
     - `"times"`: numpy array of time values (in seconds)
     - `"sr"`: sample rate
     - `"filename"`: audio filename
     - `"audio"`: raw audio array
   - Returns `True` on success, `False` on failure
   - Prints status messages if `print_output=True`

3. **`_get_xy(self, shared_data: Dict[str, Any]) -> Optional[Tuple[np.ndarray, np.ndarray]]`**
   - Hook method called by the `Curve` base class during rendering
   - Returns tuple `(times, onset_strength)` from `self._data`
   - Returns `None` if no data is loaded

4. **`draw(self, ax: Axes, shared_data: Dict[str, Any]) -> Tuple[List, List]`** *(new)*
   - Overrides base class to set proper y-axis limits
   - Calls `super().draw()` to render the curve line
   - Sets axis labels: "Time (s)" on x-axis, "Onset Strength" on y-axis
   - Sets y-limits from 0.0 to `max(onset_strength) × 1.15`
     - **Why:** Onset strength is always non-negative (energy measure), so starting from 0 eliminates wasted negative space
     - **15% padding:** Provides breathing room above peak values
   - Adds matplotlib ticker locators for time axis (major: 5s, minor: 1s)
   - Updates `shared_data` with loaded audio metadata
   - Returns `(lines, labels)` tuple for visualization tracking

## Files Modified

### `src/functions/Audio_Layers.py`
- **Removed:** The complete `OnsetNovelty` class that was previously at lines 300–352
- **Reason:** Moved to separate `OnsetNovelty_Layer.py` module for better organization
- File now ends with the `Waveform` class implementation

### `src/functions/__init__.py`
- **Before:**
  ```python
  ''' Spectrogram, Chromagram, Waveform and OnsetNovelty layers '''
  from .Audio_Layers import MelSpec, Chromagram, Waveform, OnsetNovelty
  ```
- **After:**
  ```python
  ''' Spectrogram, Chromagram, and Waveform layers '''
  from .Audio_Layers import MelSpec, Chromagram, Waveform

  ''' OnsetNovelty layer '''
  from .OnsetNovelty_Layer import OnsetNovelty
  ```
- **Effect:** `OnsetNovelty` is now imported from the new module but remains accessible via `from src.functions import OnsetNovelty`

## Design Pattern

The implementation follows LayerIt's extensibility pattern:

1. **Inheritance:** Subclasses `Curve`, not `Layer` directly
   - `Curve` is a 2D line shape primitive (see `src/functions/shapes.py`)
   - Minimal code required; most rendering is inherited

2. **Data Loading:** Implements `load_data()` hook
   - Accepts `audio_path` and optional `print_output`
   - Stores computed data in `self._data` dictionary
   - Consistent with `Waveform`, `Chromagram`, and `MelSpec` patterns

3. **Rendering Hook:** Implements `_get_xy()` to supply data
   - Returns `(times, values)` tuple for the curve to plot
   - Base class `Curve` handles coordinate transformation and polyline rendering

4. **Custom Draw Method:** Overrides `draw()` only to set proper axis limits
   - Called after the Curve base class renders the line
   - Sets non-negative y-limits (0.0 to max + 15% padding) because onset strength is always ≥ 0
   - Sets axis labels, title, and ticker locators for consistent appearance
   - Does NOT override `to_svg_group()` — still relies on inherited SVG generation

## Usage Example

```python
from src.functions import OnsetNovelty, Visualizer

# Create a visualizer
fig = Visualizer(audio="audio.wav", score="score.svg", maps="maps.json")

# Add a panel with OnsetNovelty layer
onset_layer = OnsetNovelty(color="darkorange", line_width=0.7, alpha=0.9)
fig.add_panel(onset_layer, other_layers_here)

# Compose to SVG
fig.compose("output.svg", print_output=True)
```

Before adding a panel, call `load_data()`:
```python
onset_layer.load_data("audio.wav", print_output=True)
```

## Dependencies

- **librosa:** For audio loading and onset strength computation
- **numpy:** For array operations
- **matplotlib:** For axis rendering (inherited from Curve)

## Computational Details

- **Onset Strength:** Uses `librosa.onset.onset_strength()` with default parameters
- **Hop Length:** Fixed at 512 samples (consistent with other frame-based layers)
- **Output:** One value per frame; approximately 43 frames per second at 22 kHz sample rate
- **Value Range:** Always non-negative (0.0 to ~10.0 typical), representing energy/activity

## Y-Axis Scaling

The `draw()` method sets y-limits dynamically based on the loaded onset strength data:

```python
onset_max = float(np.max(self._data["onset_strength"]))
y_upper = onset_max * 1.15 if onset_max > 0 else 1.0
ax.set_ylim(0.0, y_upper)
```

**How it works:**
- Lower bound is always **0.0** (since onset strength is non-negative)
- Upper bound is **max(onset_strength) × 1.15** (15% padding above peak)
- If max value is 0 or invalid, defaults to 1.0 as fallback
- This ensures all data is visible and properly scaled within the axis range

## Verification Checklist

✅ Subclasses `Curve` (not `Layer`)  
✅ Implements `__init__`, `load_data`, `_get_xy`, and `draw`  
✅ Overrides only `draw()` (for axis limits); does NOT override `to_svg_group()`  
✅ Stores data in `self._data` dictionary  
✅ Returns `(times, values)` tuple from `_get_xy`  
✅ No modifications to `visualization_system.py` or `shapes.py`  
✅ No modifications to existing layer classes  
✅ Standalone module in `src/functions/` directory  
✅ Properly exported in `__init__.py`  
✅ Y-axis limits (0.0 to max + 15% padding) appropriate for non-negative onset strength
