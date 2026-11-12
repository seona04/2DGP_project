import TUK_logo_mode

from pico2d import (
    SDL_KEYDOWN,
    SDL_QUIT,
    SDLK_ESCAPE,
    clear_canvas,
    close_canvas,
    delay,
    get_events,
    open_canvas,
    update_canvas,
)


def main():
    open_canvas(800, 600)
    running = TUK_logo_mode.run()

    while running:
        for event in get_events():
            if event.type == SDL_QUIT:
                running = False
            elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                running = False

        clear_canvas()
        update_canvas()
        delay(0.01)

    close_canvas()


if __name__ == "__main__":
    main()