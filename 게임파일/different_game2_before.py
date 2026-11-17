from pathlib import Path

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
from timer_ui import (
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    TIMER_FRAME_COUNT,
    draw_timer_frame,
    prepare_timer_sprite,
)


def run():
    image = load_image(
        str(Path(__file__).with_name("different_game2_before.png"))
    )
    timer_sprite = load_image(
        str(Path(__file__).with_name("timer_animation_sprite.png"))
    )
    prepare_timer_sprite(timer_sprite)

    while True:
        for event in get_events():
            if event.type == SDL_QUIT:
                return "exit"
            if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                return "exit"

        clear_canvas()
        image.draw(
            CANVAS_WIDTH // 2,
            CANVAS_HEIGHT // 2,
            CANVAS_WIDTH,
            CANVAS_HEIGHT,
        )
        timer_sprite.opacify(1.0)
        draw_timer_frame(timer_sprite, TIMER_FRAME_COUNT - 1)
        update_canvas()
        delay(0.01)
