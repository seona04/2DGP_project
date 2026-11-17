from pathlib import Path

from pico2d import (
    SDL_BLENDMODE_BLEND,
    SDL_KEYDOWN,
    SDL_MOUSEBUTTONDOWN,
    SDL_QUIT,
    SDL_SetTextureBlendMode,
    SDLK_ESCAPE,
    SDLK_SPACE,
    clear_canvas,
    delay,
    get_events,
    load_image,
    update_canvas,
)


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
BUTTON_SCALE = 0.4
BUTTON_GAP = 10
BUTTON_RIGHT_MARGIN = 16
BUTTON_TOP_MARGIN = 16


def _enable_alpha(image):
    result = SDL_SetTextureBlendMode(image.texture, SDL_BLENDMODE_BLEND)
    if result != 0:
        raise RuntimeError(f"Could not enable image alpha blending: SDL error {result}")


def _load_overlays(dialogue_file):
    if dialogue_file is None:
        return None

    dialogue = load_image(str(Path(__file__).with_name(dialogue_file)))
    pause_button = load_image(str(Path(__file__).with_name("button_pause.png")))
    skip_button = load_image(str(Path(__file__).with_name("button_skip.png")))
    for overlay in (dialogue, pause_button, skip_button):
        _enable_alpha(overlay)

    return dialogue, pause_button, skip_button


def _draw_overlays(overlays):
    if overlays is None:
        return

    dialogue, pause_button, skip_button = overlays
    dialogue_width = CANVAS_WIDTH
    dialogue_height = dialogue_width * dialogue.h / dialogue.w

    pause_width = pause_button.w * BUTTON_SCALE
    pause_height = pause_button.h * BUTTON_SCALE
    skip_width = skip_button.w * BUTTON_SCALE
    skip_height = skip_button.h * BUTTON_SCALE
    button_center_y = (
        CANVAS_HEIGHT
        - BUTTON_TOP_MARGIN
        - max(pause_height, skip_height) / 2
    )
    pause_x = (
        CANVAS_WIDTH
        - BUTTON_RIGHT_MARGIN
        - skip_width
        - BUTTON_GAP
        - pause_width / 2
    )
    skip_x = CANVAS_WIDTH - BUTTON_RIGHT_MARGIN - skip_width / 2

    dialogue.draw(
        CANVAS_WIDTH // 2,
        dialogue_height / 2,
        dialogue_width,
        dialogue_height,
    )
    pause_button.draw(pause_x, button_center_y, pause_width, pause_height)
    skip_button.draw(skip_x, button_center_y, skip_width, skip_height)


def run_image(image_file, dialogue_file=None):
    image = load_image(str(Path(__file__).with_name(image_file)))
    overlays = _load_overlays(dialogue_file)

    while True:
        for event in get_events():
            if event.type == SDL_QUIT:
                return "exit"
            if event.type == SDL_KEYDOWN:
                if event.key == SDLK_ESCAPE:
                    return "exit"
                if event.key == SDLK_SPACE:
                    return "next"
            if event.type == SDL_MOUSEBUTTONDOWN:
                return "next"

        clear_canvas()
        image.draw(
            CANVAS_WIDTH // 2,
            CANVAS_HEIGHT // 2,
            CANVAS_WIDTH,
            CANVAS_HEIGHT,
        )
        _draw_overlays(overlays)
        update_canvas()
        delay(0.01)
