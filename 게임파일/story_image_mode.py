from pathlib import Path
from time import monotonic

import pause_mode
from pico2d import (
    SDL_BLENDMODE_BLEND,
    SDL_BUTTON_LEFT,
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
DIALOGUE_FADE_DURATION = 1.0


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


def _draw_overlays(overlays, dialogue_opacity=1.0):
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

    dialogue.opacify(dialogue_opacity)
    dialogue.draw(
        CANVAS_WIDTH // 2,
        dialogue_height / 2,
        dialogue_width,
        dialogue_height,
    )
    pause_button.draw(pause_x, button_center_y, pause_width, pause_height)
    skip_button.draw(skip_x, button_center_y, skip_width, skip_height)


def _pause_button_contains(mouse_x, mouse_y, overlays):
    if overlays is None:
        return False

    _, pause_button, skip_button = overlays
    pause_width = pause_button.w * BUTTON_SCALE
    pause_height = pause_button.h * BUTTON_SCALE
    skip_height = skip_button.h * BUTTON_SCALE
    button_center_y = (
        CANVAS_HEIGHT
        - BUTTON_TOP_MARGIN
        - max(pause_height, skip_height) / 2
    )
    pause_x = (
        CANVAS_WIDTH
        - BUTTON_RIGHT_MARGIN
        - skip_button.w * BUTTON_SCALE
        - BUTTON_GAP
        - pause_width / 2
    )
    left = pause_x - pause_width / 2
    right = pause_x + pause_width / 2
    top = CANVAS_HEIGHT - button_center_y - pause_height / 2
    bottom = CANVAS_HEIGHT - button_center_y + pause_height / 2
    return left <= mouse_x < right and top <= mouse_y < bottom


def _draw_scene(image, overlays, dialogue_opacity):
    clear_canvas()
    image.draw(
        CANVAS_WIDTH // 2,
        CANVAS_HEIGHT // 2,
        CANVAS_WIDTH,
        CANVAS_HEIGHT,
    )
    _draw_overlays(overlays, dialogue_opacity)


def run_image(image_file, dialogue_file=None):
    image = load_image(str(Path(__file__).with_name(image_file)))
    overlays = _load_overlays(dialogue_file)
    dialogue_fade_start = monotonic()

    while True:
        for event in get_events():
            if event.type == SDL_QUIT:
                return "exit"
            if event.type == SDL_KEYDOWN:
                if event.key == SDLK_ESCAPE:
                    return "exit"
                if event.key == SDLK_SPACE:
                    return "next"
            if (
                event.type == SDL_MOUSEBUTTONDOWN
                and event.button == SDL_BUTTON_LEFT
                and _pause_button_contains(event.x, event.y, overlays)
            ):
                dialogue_opacity = min(
                    (monotonic() - dialogue_fade_start) / DIALOGUE_FADE_DURATION,
                    1.0,
                )
                result = pause_mode.run(
                    lambda: _draw_scene(image, overlays, dialogue_opacity)
                )
                if result == "exit":
                    return result
                if result != "resume":
                    raise RuntimeError(f"Unexpected result from pause mode: {result}")
            elif event.type == SDL_MOUSEBUTTONDOWN:
                return "next"

        dialogue_opacity = min(
            (monotonic() - dialogue_fade_start) / DIALOGUE_FADE_DURATION,
            1.0,
        )
        _draw_scene(image, overlays, dialogue_opacity)
        update_canvas()
        delay(0.01)
