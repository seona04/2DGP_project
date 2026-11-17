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
TIMER_DURATION = 120.0
TIMER_COLUMNS = 3
TIMER_ROWS = 4
TIMER_FRAME_COUNT = TIMER_COLUMNS * TIMER_ROWS
TIMER_WIDTH = 225
TIMER_RIGHT_MARGIN = 64
TIMER_TOP_MARGIN = 10


def _timer_frame_index(elapsed):
    progress = min(max(elapsed / TIMER_DURATION, 0.0), 1.0)
    return min(int(progress * (TIMER_FRAME_COUNT - 1)), TIMER_FRAME_COUNT - 1)


def _draw_timer(sprite, elapsed):
    frame_width = sprite.w // TIMER_COLUMNS
    frame_height = sprite.h // TIMER_ROWS
    frame_index = _timer_frame_index(elapsed)
    column = frame_index % TIMER_COLUMNS
    row_from_top = frame_index // TIMER_COLUMNS
    frame_left = column * frame_width
    frame_bottom = sprite.h - (row_from_top + 1) * frame_height
    draw_height = TIMER_WIDTH * frame_height / frame_width
    draw_center_x = CANVAS_WIDTH - TIMER_RIGHT_MARGIN - TIMER_WIDTH / 2
    draw_center_y = (
        CANVAS_HEIGHT - TIMER_TOP_MARGIN - draw_height / 2
    )
    sprite.clip_draw(
        frame_left,
        frame_bottom,
        frame_width,
        frame_height,
        draw_center_x,
        draw_center_y,
        TIMER_WIDTH,
        draw_height,
    )


def run():
    image = load_image(
        str(Path(__file__).with_name("different_game1_after.png"))
    )
    timer_sprite = load_image(
        str(Path(__file__).with_name("timer_animation_sprite.png"))
    )
    result = SDL_SetTextureBlendMode(
        timer_sprite.texture, SDL_BLENDMODE_BLEND
    )
    if result != 0:
        raise RuntimeError(
            f"Could not enable timer alpha blending: SDL error {result}"
        )
    if timer_sprite.w % TIMER_COLUMNS or timer_sprite.h % TIMER_ROWS:
        raise RuntimeError("Timer sprite dimensions do not match its 3x4 frame grid")
    start_time = monotonic()

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
        _draw_timer(timer_sprite, monotonic() - start_time)
        update_canvas()
        delay(0.01)
