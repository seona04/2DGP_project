from pico2d import (
    SDL_KEYDOWN,
    SDL_QUIT,
    SDLK_ESCAPE,
    clear_canvas,
    delay,
    get_events,
    update_canvas,
)


def run():
    while True:
        for event in get_events():
            if event.type == SDL_QUIT:
                return "exit"
            if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                return "exit"

        clear_canvas()
        update_canvas()
        delay(0.01)
