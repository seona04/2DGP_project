from pathlib import Path

from pico2d import (
    SDL_BUTTON_LEFT,
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
CLOSE_BUTTON_BOUNDS = (0.92, 0.02, 0.99, 0.15)


def _clicked_close_button(mouse_x, mouse_y):
    left, top, right, bottom = CLOSE_BUTTON_BOUNDS
    return (
        CANVAS_WIDTH * left <= mouse_x < CANVAS_WIDTH * right
        and CANVAS_HEIGHT * top <= mouse_y < CANVAS_HEIGHT * bottom
    )


def run():
    image = load_image(str(Path(__file__).with_name("different_rule.png")))

    while True:
        for event in get_events():
            if event.type == SDL_QUIT:
                return "exit"
            if event.type == SDL_KEYDOWN:
                if event.key == SDLK_ESCAPE:
                    return "exit"
                if event.key == SDLK_SPACE:
                    return "title_ui"
            if (
                event.type == SDL_MOUSEBUTTONDOWN
                and event.button == SDL_BUTTON_LEFT
                and _clicked_close_button(event.x, event.y)
            ):
                return "title_ui"

        clear_canvas()
        image.draw(
            CANVAS_WIDTH // 2,
            CANVAS_HEIGHT // 2,
            CANVAS_WIDTH,
            CANVAS_HEIGHT,
        )
        update_canvas()
        delay(0.01)
