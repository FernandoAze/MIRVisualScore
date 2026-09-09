import sys
from pathlib import Path

# Add parent directory to path so we can import src
script_dir = Path(__file__).parent
root_dir = script_dir.parent
sys.path.insert(0, str(root_dir))
input_parent_dir = str("src/input_files/BWV856/Performance1")

from src.functions import *

audio_file = str(root_dir / input_parent_dir / "BWV856_AndrasSchiff.wav")
svg_score_all_onsets = str(root_dir / input_parent_dir / "SW andras.svg")
svg_score_sparse_onsets = str(root_dir / input_parent_dir / "BWV856_ANDRAS_SPARSE.svg")
maps_file_all_onsets = str(root_dir / input_parent_dir / "andras.maps.json")
maps_file_sparse_onsets = str(root_dir / input_parent_dir / "andras_FEW_ONSETS.maps.json")
beat_file = str(root_dir / input_parent_dir / "beat_example1.npz")

fig = Visualizer(audio=audio_file, score=svg_score_all_onsets, maps=maps_file_all_onsets, beats=beat_file)

fig.add_panel(Waveform(color=(0, 0, 1), normalize=True), BeatsLayer(line_width=0.7), Onset(onset_color=(0,0,0), line_width=0.5), height_scale=0.5)

SVG_fig = fig.compose("Full_BWV856.svg", print_output=True) 

fig_sparse = Visualizer(audio=audio_file, score=svg_score_sparse_onsets, maps=maps_file_sparse_onsets, beats=beat_file)

fig_sparse.add_panel(Waveform(color=(0, 0, 1), normalize=True), BeatsLayer(line_width=0.7), Onset(onset_color=(0,0,0), line_width=0.5), height_scale=0.5)

SVG_fig_sparse = fig_sparse.compose("SPARSE_BWV856.svg", print_output=True)

svg_Layer_Width = Visualizer().get_SVG_Root_Dimensions(SVG_fig_sparse)[0]
svg_Layer_Height = Visualizer().get_SVG_Root_Dimensions(SVG_fig_sparse)[1]

# vvvvvvvvvvvvvvv FOR STACKING SCORES IN SAME VISUALIZATION vvvvvvvvvvvvvvv
import xml.etree.ElementTree as ET
def stack_svgs_verbatim(svg_paths_with_offsets, width, height, output_path):
    # Nests each composed SVG's content unmodified, avoiding id-rewrite collisions with CSS selectors baked into each score's <style> block
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')

    nested_svgs = []
    for svg_path, y_offset in svg_paths_with_offsets:
        root = ET.parse(svg_path).getroot()
        children_markup = '\n'.join(ET.tostring(child, encoding='unicode') for child in root)
        nested_svgs.append(
            f'<svg x="0" y="{y_offset}" width="{root.get("width")}" height="{root.get("height")}" '
            f'overflow="visible">{children_markup}</svg>'
        )

    final_markup = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{width}px" height="{height}px" viewBox="0 0 {width} {height}">
  <rect x="0" y="0" width="100%" height="100%" fill="#ffffff" />
{chr(10).join(nested_svgs)}
</svg>'''

    with open(output_path, 'w', encoding='UTF-8') as f:
        f.write(final_markup)
    return output_path
# ^^^^^^^^^^^^^^ FOR STACKING SCORES IN SAME VISUALIZATION ^^^^^^^^^^^^^^ 
stack_svgs_verbatim(
    [
        
        (str(root_dir / "output" / "Full_BWV856.svg"), svg_Layer_Height),
        (str(root_dir / "output" / "SPARSE_BWV856.svg"), 0)
    ],
    width=svg_Layer_Width + 300,
    height=svg_Layer_Height * 3,
    output_path=str(root_dir / "output" / "FINAL_combined.svg"),
)
