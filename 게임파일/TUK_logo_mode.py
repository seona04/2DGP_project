from pathlib import Path
from time import monotonic

from pico2d import (
    SDL_KEYDOWN,
    SDL_QUIT,
    SDLK_ESCAPE,
    clear_canvas,
    delay,
    get_events,
    load_image,
    update_canvas,
)


LOGO_DISPLAY_TIME = 2.0
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600


def run():
    logo = load_image(str(Path(__file__).with_name("TUK_logo.png")))
    start_time = monotonic()
    running = True

    while running and monotonic() - start_time < LOGO_DISPLAY_TIME:
        for event in get_events():
            if event.type == SDL_QUIT:
                running = False
            elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                running = False

        clear_canvas()
        logo.draw(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2)
        update_canvas()
        delay(0.01)

    return running