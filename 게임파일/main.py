import TUK_logo_mode
import game_story_mode
import settings_mode
import title_mode
import title_UI_mode

from pico2d import (
    close_canvas,
    open_canvas,
)


def main():
    open_canvas(800, 600)
    running = TUK_logo_mode.run()
    if running:
        running = title_mode.run()

    if running:
        mode = "title_ui"
        while mode != "exit":
            if mode == "title_ui":
                mode = title_UI_mode.run()
            elif mode == "game_story":
                mode = game_story_mode.run()
            elif mode == "settings":
                mode = settings_mode.run()
            else:
                raise RuntimeError(f"Unknown screen mode: {mode}")

    close_canvas()


if __name__ == "__main__":
    main()