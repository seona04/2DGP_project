from pathlib import Path
from time import monotonic

import different_game2_before
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
from timer_ui import (
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    TIMER_COLUMNS,
    TIMER_FRAME_COUNT,
    TIMER_LEFT_MARGIN,
    TIMER_ROWS,
    TIMER_TOP_MARGIN,
    TIMER_WIDTH,
    draw_timer_frame,
    prepare_timer_sprite,
)


TIMER_DURATION = 120.0
ITEM_GAP = 0


def _timer_frame_state(elapsed):
    progress = min(max(elapsed / TIMER_DURATION, 0.0), 1.0)
    frame_position = progress * (TIMER_FRAME_COUNT - 1)
    frame_index = int(frame_position)
    next_frame_index = min(frame_index + 1, TIMER_FRAME_COUNT - 1)
    return frame_index, next_frame_index, frame_position - frame_index


def _draw_timer(sprite, elapsed):
    frame_index, next_frame_index, opacity = _timer_frame_state(elapsed)
    sprite.opacify(1.0)
    draw_timer_frame(sprite, frame_index)
    if next_frame_index != frame_index and opacity > 0:
        sprite.opacify(opacity)
        draw_timer_frame(sprite, next_frame_index)
    sprite.opacify(1.0)


def _enable_alpha(image, label):
    result = SDL_SetTextureBlendMode(image.texture, SDL_BLENDMODE_BLEND)
    if result != 0:
        raise RuntimeError(
            f"Could not enable {label} alpha blending: SDL error {result}"
        )


def _draw_timer_items(hint_icon, timer_icon, timer_sprite):
    frame_width = timer_sprite.w // TIMER_COLUMNS
    frame_height = timer_sprite.h // TIMER_ROWS
    item_height = TIMER_WIDTH * frame_height / frame_width
    item_left = TIMER_LEFT_MARGIN + TIMER_WIDTH + ITEM_GAP
    top = TIMER_TOP_MARGIN

    for item in (hint_icon, timer_icon):
        item_width = item_height * item.w / item.h
        item.draw(
            item_left + item_width / 2,
            CANVAS_HEIGHT - top - item_height / 2,
            item_width,
            item_height,
        )
        item_left += item_width + ITEM_GAP


def run():
    image = load_image(
        str(Path(__file__).with_name("different_game1_after.png"))
    )
    timer_sprite = load_image(
        str(Path(__file__).with_name("timer_animation_sprite.png"))
    )
    prepare_timer_sprite(timer_sprite)
    hint_icon = load_image(str(Path(__file__).with_name("item_hint.png")))
    timer_icon = load_image(str(Path(__file__).with_name("item_timer.png")))
    for asset, label in (
        (hint_icon, "hint icon"),
        (timer_icon, "timer icon"),
    ):
        _enable_alpha(asset, label)
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
        elapsed = monotonic() - start_time
        _draw_timer(timer_sprite, elapsed)
        _draw_timer_items(hint_icon, timer_icon, timer_sprite)
        update_canvas()
        if elapsed >= TIMER_DURATION:
            return different_game2_before.run()
        delay(0.01)
