from pathlib import Path

import different_rule_mode
import story1_mode
import story2_mode
import story3_mode
import story4_mode
import story5_mode
import story6_mode


STORY_MODULES = (
    story1_mode,
    story2_mode,
    story3_mode,
    story4_mode,
    story5_mode,
    story6_mode,
)


def _image_number(story_module):
    image_stem = Path(story_module.IMAGE_FILE).stem
    return int(image_stem.removeprefix("story"))


def run():
    for story_module in sorted(STORY_MODULES, key=_image_number):
        result = story_module.run()
        if result == "exit":
            return result
        if result != "next":
            raise RuntimeError(
                f"Unexpected result from {story_module.__name__}: {result}"
            )

    return different_rule_mode.run()
