from pathlib import Path

import title_UI_mode
from pico2d import load_image


def run():
    title = load_image(str(Path(__file__).with_name("title.png")))
    return title_UI_mode.transition_from_title(title)
