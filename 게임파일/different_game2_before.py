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
    TIMER_DURATION,
    TIMER_FRAME_COUNT,
    draw_timer_frame,
    prepare_timer_sprite,
)


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
O_MARKER_PADDING = 12
CLICK_REGIONS = {
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


def _animation_frame_index(elapsed, frame_count):
    frame_interval = TIMER_DURATION / PAINTING_FRAME_COUNT
    return min(
        max(int(max(elapsed, 0.0) / frame_interval), 0),
        frame_count - 1,
    )


def _enable_overlay_alpha(sprite, label):
    result = SDL_SetTextureBlendMode(sprite.texture, SDL_BLENDMODE_BLEND)
    if result != 0:
        raise RuntimeError(
            f"Could not enable {label} alpha blending: SDL error {result}"
        )


def _draw_painting_frame(sprite, elapsed):
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


def _draw_pocketwatch_frame(sprite, elapsed):
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


def _draw_toolbox_frame(sprite, elapsed):
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


def _draw_screw_frame(sprite, elapsed):
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


def run():
    image = load_image(
        str(Path(__file__).with_name("different_game2_before.png"))
    )
    timer_sprite = load_image(
        str(Path(__file__).with_name("timer_animation_sprite.png"))
    )
    prepare_timer_sprite(timer_sprite)
    painting_sprite = load_image(
        str(Path(__file__).with_name("액자_animation_sprite.png"))
    )
    if (
        painting_sprite.w % PAINTING_FRAME_COUNT
        or painting_sprite.h < PAINTING_SOURCE_TOP + PAINTING_SOURCE_HEIGHT
    ):
        raise RuntimeError("Painting sprite dimensions do not match its six-frame layout")
    _enable_overlay_alpha(painting_sprite, "painting sprite")
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
    _enable_overlay_alpha(pocketwatch_sprite, "pocketwatch sprite")
    toolbox_sprite = load_image(
        str(Path(__file__).with_name("공구함_animation_sprite.png"))
    )
    if (
        toolbox_sprite.w < TOOLBOX_FRAME_COUNT * TOOLBOX_FRAME_WIDTH
        or toolbox_sprite.h < TOOLBOX_SOURCE_TOP + TOOLBOX_SOURCE_HEIGHT
    ):
        raise RuntimeError(
            "Toolbox sprite dimensions do not match its seven-frame layout"
        )
    _enable_overlay_alpha(toolbox_sprite, "toolbox sprite")
    screw_sprite = load_image(
        str(Path(__file__).with_name("나사_animation_sprite.png"))
    )
    if (
        screw_sprite.w < SCREW_FRAME_COUNT * SCREW_FRAME_WIDTH
        or screw_sprite.h < SCREW_SOURCE_TOP + SCREW_SOURCE_HEIGHT
    ):
        raise RuntimeError(
            "Screw sprite dimensions do not match its six-frame layout"
        )
    _enable_overlay_alpha(screw_sprite, "screw sprite")
    o_marker = load_image(str(Path(__file__).with_name("O_ui.png")))
    _enable_overlay_alpha(o_marker, "click marker")
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
        _draw_painting_frame(painting_sprite, elapsed)
        _draw_pocketwatch_frame(pocketwatch_sprite, elapsed)
        _draw_toolbox_frame(toolbox_sprite, elapsed)
        _draw_screw_frame(screw_sprite, elapsed)
        _draw_click_markers(o_marker, marked_regions)
        timer_sprite.opacify(1.0)
        draw_timer_frame(timer_sprite, TIMER_FRAME_COUNT - 1)
        update_canvas()
        delay(0.01)
