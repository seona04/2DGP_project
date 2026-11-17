from pathlib import Path

from pico2d import (
    SDL_KEYDOWN,
    SDL_MOUSEBUTTONDOWN,
    SDL_QUIT,
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


def run_image(image_file):
    image = load_image(str(Path(__file__).with_name(image_file)))

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
        update_canvas()
        delay(0.01)
