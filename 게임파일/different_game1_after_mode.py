from pathlib import Path
from time import monotonic

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
OVERLAY_FADE_DURATION = 2.0
PAINTING_FRAME_COUNT = 6
PAINTING_SOURCE_TOP = 210
PAINTING_SOURCE_HEIGHT = 325
PAINTING_CENTER_X = 282
PAINTING_CENTER_Y = 451
PAINTING_WIDTH = 108
PAINTING_HEIGHT = 144
POCKETWATCH_FRAME_COUNT = 7
POCKETWATCH_FRAME_START_X = 276
POCKETWATCH_FRAME_WIDTH = 270
POCKETWATCH_SOURCE_TOP = 260
POCKETWATCH_SOURCE_HEIGHT = 190
POCKETWATCH_CENTER_X = 409
POCKETWATCH_CENTER_Y = 245
POCKETWATCH_WIDTH = 68
POCKETWATCH_HEIGHT = 58
TOOLBOX_FRAME_COUNT = 6
TOOLBOX_FRAME_WIDTH = 362
TOOLBOX_SOURCE_TOP = 200
TOOLBOX_SOURCE_HEIGHT = 320
TOOLBOX_CENTER_X = 657
TOOLBOX_CENTER_Y = 128
TOOLBOX_WIDTH = 121
TOOLBOX_HEIGHT = 143
SCREW_FRAME_COUNT = 6
SCREW_FRAME_WIDTH = 362
SCREW_SOURCE_TOP = 340
SCREW_SOURCE_HEIGHT = 110
SCREW_CENTER_X = 642
SCREW_CENTER_Y = 50
SCREW_WIDTH = 75
SCREW_HEIGHT = 25
GLOVE_FRAME_COUNT = 5
GLOVE_FRAME_WIDTH = 434
GLOVE_SOURCE_TOP = 250
GLOVE_SOURCE_HEIGHT = 260
GLOVE_CENTER_X = 678
GLOVE_CENTER_Y = 252
GLOVE_WIDTH = 54
GLOVE_HEIGHT = 27
O_MARKER_SIZE = 54
CLICK_REGIONS = {
    "display_case": (
        OBJECT_CENTER_X,
        OBJECT_CENTER_Y,
        OBJECT_WIDTH,
        OBJECT_HEIGHT,
    ),
    "glove": (GLOVE_CENTER_X, GLOVE_CENTER_Y, GLOVE_WIDTH, GLOVE_HEIGHT),
    "painting": (
        PAINTING_CENTER_X,
        PAINTING_CENTER_Y,
        PAINTING_WIDTH,
        PAINTING_HEIGHT,
    ),
    "pocketwatch": (
        POCKETWATCH_CENTER_X,
        POCKETWATCH_CENTER_Y,
        POCKETWATCH_WIDTH,
        POCKETWATCH_HEIGHT,
    ),
    "toolbox": (
        TOOLBOX_CENTER_X,
        TOOLBOX_CENTER_Y,
        TOOLBOX_WIDTH,
        TOOLBOX_HEIGHT,
    ),
    "screws": (SCREW_CENTER_X, SCREW_CENTER_Y, SCREW_WIDTH, SCREW_HEIGHT),
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
    progress = min(max(elapsed / TIMER_DURATION, 0.0), 1.0)
    return min(int(progress * frame_count), frame_count - 1)


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


def _draw_painting(sprite, elapsed):
    frame_width = sprite.w // PAINTING_FRAME_COUNT
    frame_bottom = sprite.h - PAINTING_SOURCE_TOP - PAINTING_SOURCE_HEIGHT
    sprite.clip_draw(
        _animation_frame_index(elapsed, PAINTING_FRAME_COUNT) * frame_width,
        frame_bottom,
        frame_width,
        PAINTING_SOURCE_HEIGHT,
        PAINTING_CENTER_X,
        PAINTING_CENTER_Y,
        PAINTING_WIDTH,
        PAINTING_HEIGHT,
    )


def _draw_pocketwatch(sprite, elapsed):
    frame_bottom = sprite.h - POCKETWATCH_SOURCE_TOP - POCKETWATCH_SOURCE_HEIGHT
    sprite.clip_draw(
        POCKETWATCH_FRAME_START_X
        + _animation_frame_index(elapsed, POCKETWATCH_FRAME_COUNT)
        * POCKETWATCH_FRAME_WIDTH,
        frame_bottom,
        POCKETWATCH_FRAME_WIDTH,
        POCKETWATCH_SOURCE_HEIGHT,
        POCKETWATCH_CENTER_X,
        POCKETWATCH_CENTER_Y,
        POCKETWATCH_WIDTH,
        POCKETWATCH_HEIGHT,
    )


def _draw_toolbox(sprite, elapsed):
    frame_bottom = sprite.h - TOOLBOX_SOURCE_TOP - TOOLBOX_SOURCE_HEIGHT
    sprite.clip_draw(
        _animation_frame_index(elapsed, TOOLBOX_FRAME_COUNT)
        * TOOLBOX_FRAME_WIDTH,
        frame_bottom,
        TOOLBOX_FRAME_WIDTH,
        TOOLBOX_SOURCE_HEIGHT,
        TOOLBOX_CENTER_X,
        TOOLBOX_CENTER_Y,
        TOOLBOX_WIDTH,
        TOOLBOX_HEIGHT,
    )


def _draw_screws(sprite, elapsed):
    frame_bottom = sprite.h - SCREW_SOURCE_TOP - SCREW_SOURCE_HEIGHT
    sprite.clip_draw(
        _animation_frame_index(elapsed, SCREW_FRAME_COUNT)
        * SCREW_FRAME_WIDTH,
        frame_bottom,
        SCREW_FRAME_WIDTH,
        SCREW_SOURCE_HEIGHT,
        SCREW_CENTER_X,
        SCREW_CENTER_Y,
        SCREW_WIDTH,
        SCREW_HEIGHT,
    )


def _draw_fading_overlay(sprite, draw_frame, elapsed, opacity):
    sprite.opacify(opacity)
    draw_frame(sprite, elapsed)
    sprite.opacify(1.0)


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
        center_x, center_y, _, _ = region
        marker.draw(
            center_x,
            center_y,
            O_MARKER_SIZE,
            O_MARKER_SIZE,
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
    display_case_sprite = load_image(
        str(Path(__file__).with_name("진열장_animation_sprite.png"))
    )
    _enable_alpha(display_case_sprite, "display case sprite")
    if display_case_sprite.w % OBJECT_FRAME_COUNT:
        raise RuntimeError("Display case sprite must contain six equal-width frames")
    painting_sprite = load_image(
        str(Path(__file__).with_name("액자_animation_sprite.png"))
    )
    if (
        painting_sprite.w % PAINTING_FRAME_COUNT
        or painting_sprite.h < PAINTING_SOURCE_TOP + PAINTING_SOURCE_HEIGHT
    ):
        raise RuntimeError("Painting sprite dimensions do not match its six-frame layout")
    _enable_alpha(painting_sprite, "painting sprite")
    pocketwatch_sprite = load_image(
        str(Path(__file__).with_name("황금회중시계_animation_sprite.png"))
    )
    if (
        pocketwatch_sprite.w
        < POCKETWATCH_FRAME_START_X
        + POCKETWATCH_FRAME_COUNT * POCKETWATCH_FRAME_WIDTH
        or pocketwatch_sprite.h
        < POCKETWATCH_SOURCE_TOP + POCKETWATCH_SOURCE_HEIGHT
    ):
        raise RuntimeError(
            "Pocketwatch sprite dimensions do not match its seven-frame layout"
        )
    _enable_alpha(pocketwatch_sprite, "pocketwatch sprite")
    toolbox_sprite = load_image(
        str(Path(__file__).with_name("공구함_animation_sprite.png"))
    )
    if (
        toolbox_sprite.w < TOOLBOX_FRAME_COUNT * TOOLBOX_FRAME_WIDTH
        or toolbox_sprite.h < TOOLBOX_SOURCE_TOP + TOOLBOX_SOURCE_HEIGHT
    ):
        raise RuntimeError(
            "Toolbox sprite dimensions do not match its six-frame layout"
        )
    _enable_alpha(toolbox_sprite, "toolbox sprite")
    screw_sprite = load_image(
        str(Path(__file__).with_name("나사_animation_sprite.png"))
    )
    if (
        screw_sprite.w < SCREW_FRAME_COUNT * SCREW_FRAME_WIDTH
        or screw_sprite.h < SCREW_SOURCE_TOP + SCREW_SOURCE_HEIGHT
    ):
        raise RuntimeError("Screw sprite dimensions do not match its six-frame layout")
    _enable_alpha(screw_sprite, "screw sprite")
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
        overlay_opacity = min(elapsed / OVERLAY_FADE_DURATION, 1.0)
        _draw_fading_overlay(
            painting_sprite, _draw_painting, elapsed, overlay_opacity
        )
        _draw_fading_overlay(
            toolbox_sprite, _draw_toolbox, elapsed, overlay_opacity
        )
        _draw_fading_overlay(
            screw_sprite, _draw_screws, elapsed, overlay_opacity
        )
        _draw_fading_overlay(
            display_case_sprite, _draw_object, elapsed, overlay_opacity
        )
        _draw_fading_overlay(
            pocketwatch_sprite, _draw_pocketwatch, elapsed, overlay_opacity
        )
        _draw_fading_overlay(
            glove_sprite, _draw_glove, elapsed, overlay_opacity
        )
        _draw_click_markers(o_marker, marked_regions)
        _draw_timer(timer_sprite, elapsed)
        _draw_timer_items(hint_icon, timer_icon, timer_sprite)
        update_canvas()
        if elapsed >= TIMER_DURATION:
            return "different_game2_before"
        delay(0.01)
