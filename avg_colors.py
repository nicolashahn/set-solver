#!/usr/bin/env python
"""Get average shape color values for each red, green, purple card
in the labeled cards.

RESULTS (as of this commit 2018-6-21):

red (0, 34, 226)
green (64, 123, 0)
purple (89, 0, 76)

"""

import os
from classify_card import shape_rgb, pixels_mean
from common import ALL_CARDS_LABELED_DIR, mean


def main():
    all_files = os.listdir(ALL_CARDS_LABELED_DIR)

    res = []
    for color in ("red", "green", "purple"):
        color_files = [
            f for f in all_files if f.startswith(color) and f.endswith(".jpg")
        ]
        color_values = [
            shape_rgb(os.path.join(ALL_CARDS_LABELED_DIR, f)) for f in color_files
        ]
        res.append((color, pixels_mean(color_values)))
    for color, rgb in res:
        print(color, rgb)


if __name__ == "__main__":
    main()
