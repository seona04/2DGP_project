from pathlib import Path

from pico2d import (
    SDL_BLENDMODE_BLEND,
    SDL_KEYDOWN,
    SDL_MOUSEBUTTONDOWN,
    SDL_QUIT,
    SDL_SetTextureBlendMode,
    SDLK_ESCAPE,
    SDLK_SPACE,
    delay,
    get_events,
    load_image,
    update_canvas,
)


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600


def run(draw_background):
    pause_label = load_image(str(Path(__file__).with_name("button_pause.png")))
    result = SDL_SetTextureBlendMode(
        pause_label.texture, SDL_BLENDMODE_BLEND
    )
    if result != 0:
        raise RuntimeError(
            f"Could not enable image alpha blending: SDL error {result}"
        )

    while True:
        for event in get_events():
            if event.type == SDL_QUIT:
                return "exit"
            if event.type == SDL_KEYDOWN:
                if event.key == SDLK_ESCAPE:
                    return "exit"
                if event.key == SDLK_SPACE:
                    return "resume"
            if event.type == SDL_MOUSEBUTTONDOWN:
                return "resume"

        draw_background()
        pause_label.draw(
            CANVAS_WIDTH // 2,
            CANVAS_HEIGHT // 2,
            pause_label.w,
            pause_label.h,
        )
        update_canvas()
        delay(0.01)
