from pathlib import Path
from time import monotonic

import different_game2_before
from pico2d import (
    SDL_BUTTON_LEFT,
    SDL_BLENDMODE_BLEND,
    SDL_KEYDOWN,
    SDL_MOUSEBUTTONDOWN,
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
    TIMER_DURATION,
    TIMER_FRAME_COUNT,
    TIMER_LEFT_MARGIN,
    TIMER_ROWS,
    TIMER_TOP_MARGIN,
    TIMER_WIDTH,
    draw_timer_frame,
    prepare_timer_sprite,
)


ITEM_GAP = 0
OBJECT_FRAME_COUNT = 6
OBJECT_SOURCE_TOP = 190
OBJECT_SOURCE_HEIGHT = 389
OBJECT_CENTER_X = 409
OBJECT_CENTER_Y = 227
OBJECT_WIDTH = 236
OBJECT_HEIGHT = 340
ANIMATION_FRAME_DURATION = TIMER_DURATION / OBJECT_FRAME_COUNT
GLOVE_FRAME_COUNT = 5
GLOVE_FRAME_WIDTH = 434
GLOVE_SOURCE_TOP = 250
GLOVE_SOURCE_HEIGHT = 260
GLOVE_CENTER_X = 678
GLOVE_CENTER_Y = 252
GLOVE_WIDTH = 54
GLOVE_HEIGHT = 27
O_MARKER_PADDING = 12
CLICK_REGIONS = {
    "display_case": (
        OBJECT_CENTER_X,
        OBJECT_CENTER_Y,
        OBJECT_WIDTH,
        OBJECT_HEIGHT,
    ),
    "glove": (GLOVE_CENTER_X, GLOVE_CENTER_Y, GLOVE_WIDTH, GLOVE_HEIGHT),
}


def _timer_frame_state(elapsed):
    progress = min(max(elapsed / TIMER_DURATION, 0.0), 1.0)
    frame_position = progress * (TIMER_FRAME_COUNT - 1)
    frame_index = int(frame_position)
    next_frame_index = min(frame_index + 1, TIMER_FRAME_COUNT - 1)
    return frame_index, next_frame_index, frame_position - frame_index


def _object_frame_index(elapsed):
    return _animation_frame_index(elapsed, OBJECT_FRAME_COUNT)


def _animation_frame_index(elapsed, frame_count):
    return min(
        max(int(max(elapsed, 0.0) / ANIMATION_FRAME_DURATION), 0),
        frame_count - 1,
    )


def _draw_object(sprite, elapsed):
    frame_width = sprite.w // OBJECT_FRAME_COUNT
    frame_bottom = sprite.h - OBJECT_SOURCE_TOP - OBJECT_SOURCE_HEIGHT
    sprite.clip_draw(
        _object_frame_index(elapsed) * frame_width,
        frame_bottom,
        frame_width,
        OBJECT_SOURCE_HEIGHT,
        OBJECT_CENTER_X,
        OBJECT_CENTER_Y,
        OBJECT_WIDTH,
        OBJECT_HEIGHT,
    )


def _draw_glove(sprite, elapsed):
    frame_bottom = sprite.h - GLOVE_SOURCE_TOP - GLOVE_SOURCE_HEIGHT
    sprite.clip_draw(
        _animation_frame_index(elapsed, GLOVE_FRAME_COUNT) * GLOVE_FRAME_WIDTH,
        frame_bottom,
        GLOVE_FRAME_WIDTH,
        GLOVE_SOURCE_HEIGHT,
        GLOVE_CENTER_X,
        GLOVE_CENTER_Y,
        GLOVE_WIDTH,
        GLOVE_HEIGHT,
    )


def _contains_click(region, mouse_x, mouse_y):
    center_x, center_y, width, height = region
    left = center_x - width / 2
    right = center_x + width / 2
    top = CANVAS_HEIGHT - center_y - height / 2
    bottom = CANVAS_HEIGHT - center_y + height / 2
    return left <= mouse_x < right and top <= mouse_y < bottom


def _draw_click_markers(marker, marked_regions):
    for name, region in CLICK_REGIONS.items():
        if name not in marked_regions:
            continue
        center_x, center_y, width, height = region
        size = max(width, height) + O_MARKER_PADDING
        scale = size / max(marker.w, marker.h)
        marker.draw(
            center_x,
            center_y,
            marker.w * scale,
            marker.h * scale,
        )


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
    object_sprite = load_image(
        str(
            Path(__file__).with_name(
                "골드 회중시계가 등장하는 앤티크 진열장 애니메이션 스프라이트 시트-2.png"
            )
        )
    )
    _enable_alpha(object_sprite, "display case sprite")
    if object_sprite.w % OBJECT_FRAME_COUNT:
        raise RuntimeError("Display case sprite must contain six equal-width frames")
    glove_sprite = load_image(
        str(Path(__file__).with_name("장갑_animation_sprite.png"))
    )
    if (
        glove_sprite.w < GLOVE_FRAME_COUNT * GLOVE_FRAME_WIDTH
        or glove_sprite.h < GLOVE_SOURCE_TOP + GLOVE_SOURCE_HEIGHT
    ):
        raise RuntimeError("Glove sprite dimensions do not match its five-frame layout")
    _enable_alpha(glove_sprite, "glove sprite")
    hint_icon = load_image(str(Path(__file__).with_name("item_hint.png")))
    timer_icon = load_image(str(Path(__file__).with_name("item_timer.png")))
    for asset, label in (
        (hint_icon, "hint icon"),
        (timer_icon, "timer icon"),
    ):
        _enable_alpha(asset, label)
    o_marker = load_image(str(Path(__file__).with_name("O_ui.png")))
    _enable_alpha(o_marker, "click marker")
    marked_regions = set()
    start_time = monotonic()

    while True:
        for event in get_events():
            if event.type == SDL_QUIT:
                return "exit"
            if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                return "exit"
            if (
                event.type == SDL_MOUSEBUTTONDOWN
                and event.button == SDL_BUTTON_LEFT
            ):
                for name, region in CLICK_REGIONS.items():
                    if _contains_click(region, event.x, event.y):
                        marked_regions.add(name)

        clear_canvas()
        image.draw(
            CANVAS_WIDTH // 2,
            CANVAS_HEIGHT // 2,
            CANVAS_WIDTH,
            CANVAS_HEIGHT,
        )
        elapsed = monotonic() - start_time
        _draw_object(object_sprite, elapsed)
        _draw_glove(glove_sprite, elapsed)
        _draw_click_markers(o_marker, marked_regions)
        _draw_timer(timer_sprite, elapsed)
        _draw_timer_items(hint_icon, timer_icon, timer_sprite)
        update_canvas()
        if elapsed >= TIMER_DURATION:
            return different_game2_before.run()
        delay(0.01)
