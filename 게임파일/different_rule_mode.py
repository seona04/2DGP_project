from pathlib import Path

import different_game1_after_mode
import different_game2_before
from pico2d import (
    SDL_BUTTON_LEFT,
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
CLOSE_BUTTON_BOUNDS = (0.925, 0.03, 0.984, 0.138)


def _clicked_close_button(mouse_x, mouse_y):
    left, top, right, bottom = CLOSE_BUTTON_BOUNDS
    return (
        CANVAS_WIDTH * left <= mouse_x < CANVAS_WIDTH * right
        and CANVAS_HEIGHT * top <= mouse_y < CANVAS_HEIGHT * bottom
    )


def _enable_alpha(image):
    result = SDL_SetTextureBlendMode(image.texture, SDL_BLENDMODE_BLEND)
    if result != 0:
        raise RuntimeError(
            f"Could not enable image alpha blending: SDL error {result}"
        )


def run():
    image = load_image(str(Path(__file__).with_name("different_rule.png")))
    close_button = load_image(
        str(Path(__file__).with_name("button_close_overlay.png"))
    )
    _enable_alpha(close_button)

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
                result = different_game1_after_mode.run()
                if result == "different_game2_before":
                    return different_game2_before.run()
                return result

        clear_canvas()
        image.draw(
            CANVAS_WIDTH // 2,
            CANVAS_HEIGHT // 2,
            CANVAS_WIDTH,
            CANVAS_HEIGHT,
        )
        left, top, right, bottom = CLOSE_BUTTON_BOUNDS
        close_button.draw(
            CANVAS_WIDTH * (left + right) / 2,
            CANVAS_HEIGHT * (1 - (top + bottom) / 2),
            CANVAS_WIDTH * (right - left),
            CANVAS_HEIGHT * (bottom - top),
        )
        update_canvas()
        delay(0.01)
