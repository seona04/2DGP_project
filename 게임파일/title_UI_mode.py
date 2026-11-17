from pathlib import Path
from time import monotonic

from pico2d import (
    SDL_BLENDMODE_BLEND,
    SDL_KEYDOWN,
    SDL_QUIT,
    SDL_SetTextureBlendMode,
    SDLK_ESCAPE,
    clear_canvas,
    delay,
    get_events,
    load_image,
    update_canvas,
)


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
TITLE_IMAGE_WIDTH = 1672
TITLE_IMAGE_HEIGHT = 941
TRANSITION_DURATION = 2.0

BUTTONS = (
    ("button_start.png", 630, 579, 418, 104),
    ("button_settings.png", 634, 676, 410, 89),
    ("button_exit.png", 633, 763, 410, 85),
)


def _enable_opacity(image):
    result = SDL_SetTextureBlendMode(image.texture, SDL_BLENDMODE_BLEND)
    if result != 0:
        raise RuntimeError(f"Could not enable texture alpha blending: SDL error {result}")


def _load_images():
    title = load_image(str(Path(__file__).with_name("title_main.png")))
    _enable_opacity(title)
    buttons = [
        (load_image(str(Path(__file__).with_name(filename))), x, y, width, height)
        for filename, x, y, width, height in BUTTONS
    ]
    for button, _, _, _, _ in buttons:
        _enable_opacity(button)
    return title, buttons


def _draw_screen(title, buttons, opacity=1.0):
    scale_x = CANVAS_WIDTH / TITLE_IMAGE_WIDTH
    scale_y = CANVAS_HEIGHT / TITLE_IMAGE_HEIGHT

    title.opacify(opacity)
    title.draw(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2, CANVAS_WIDTH, CANVAS_HEIGHT)
    for button, x, y, width, height in buttons:
        button.opacify(opacity)
        button.draw(
            (x + width / 2) * scale_x,
            CANVAS_HEIGHT - (y + height / 2) * scale_y,
            width * scale_x,
            height * scale_y,
        )


def transition_from_title(previous_title):
    title, buttons = _load_images()
    start_time = monotonic()
    running = True

    while running:
        for event in get_events():
            if event.type == SDL_QUIT:
                running = False
            elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                running = False

        if not running:
            break

        progress = min((monotonic() - start_time) / TRANSITION_DURATION, 1.0)
        clear_canvas()
        previous_title.draw(
            CANVAS_WIDTH // 2,
            CANVAS_HEIGHT // 2,
            CANVAS_WIDTH,
            CANVAS_HEIGHT,
        )
        _draw_screen(title, buttons, progress)
        update_canvas()

        if progress >= 1.0:
            break
        delay(0.01)

    return running


def run():
    title, buttons = _load_images()
    running = True

    while running:
        for event in get_events():
            if event.type == SDL_QUIT:
                running = False
            elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                running = False

        clear_canvas()
        _draw_screen(title, buttons)
        update_canvas()
        delay(0.01)

    return running