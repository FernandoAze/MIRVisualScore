import sys
from pathlib import Path

# Add parent directory to path so we can import src
script_dir = Path(__file__).parent
root_dir = script_dir.parent
sys.path.insert(0, str(root_dir))
input_parent_dir = str("src/input_files/ClairDeLune/")

from src.functions import *

audio_file = str(root_dir / input_parent_dir / "ClairDeLune_MariaJoaoPires_untilM6.wav")
svg_score = str(root_dir / input_parent_dir / "ClairDeLune_MariaJoaoPires_untilM6.svg")
maps_file = str(root_dir / input_parent_dir / "ClairDeLune_MariaJoaoPires_untilM6.maps.json")
beat_file = str(root_dir / input_parent_dir / "Clair_Beat.npz")


fig = Visualizer(audio=audio_file, score=svg_score, maps=maps_file, beats=beat_file)

# Panel: OnsetNovelty curve combined with BeatsLayer markers
fig.add_panel(OnsetNovelty(color="darkorange", line_width=0.7, alpha=0.9), height_scale=1.0)

fig.compose("OnsetNoveltyDemo.svg", score_position=1, print_output=True)
