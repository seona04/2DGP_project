from pico2d import SDL_BLENDMODE_BLEND, SDL_SetTextureBlendMode


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
TIMER_COLUMNS = 3
TIMER_ROWS = 4
TIMER_FRAME_COUNT = TIMER_COLUMNS * TIMER_ROWS
TIMER_DURATION = 120.0
TIMER_WIDTH = 225
TIMER_LEFT_MARGIN = 16
TIMER_TOP_MARGIN = 10


def prepare_timer_sprite(sprite):
    if sprite.w % TIMER_COLUMNS or sprite.h % TIMER_ROWS:
        raise RuntimeError("Timer sprite dimensions do not match its 3x4 frame grid")

    result = SDL_SetTextureBlendMode(sprite.texture, SDL_BLENDMODE_BLEND)
    if result != 0:
        raise RuntimeError(f"Could not enable timer alpha blending: SDL error {result}")


def draw_timer_frame(sprite, frame_index):
    frame_width = sprite.w // TIMER_COLUMNS
    frame_height = sprite.h // TIMER_ROWS
    column = frame_index % TIMER_COLUMNS
    row_from_top = frame_index // TIMER_COLUMNS
    frame_left = column * frame_width
    frame_bottom = sprite.h - (row_from_top + 1) * frame_height
    draw_height = TIMER_WIDTH * frame_height / frame_width
    draw_center_x = TIMER_LEFT_MARGIN + TIMER_WIDTH / 2
    draw_center_y = CANVAS_HEIGHT - TIMER_TOP_MARGIN - draw_height / 2

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
