#!/usr/bin/env python
"""Process a card image to make it easier to match an unlabeled card to
the correct labeled card."""

import os
import sys
import cv2
import numpy as np
from common import PROCESS_CARD_OUT_DIR, write_im, display_im, shrink

from vendor import noteshrink

PROCESSED_CARD_FILENAME = "processed.jpg"


def to_pil(cv2_im):
    pass


def to_cv2(pil_im):
    pass


def blur_card(card_filename):
    im = cv2.imread(card_filename, 1)

    # filters to make it easier for opencv to find card
    blur = cv2.GaussianBlur(im, (1, 1), 1)
    filename = "%s_blurred.png" % (card_filename)
    cv2.imwrite(filename, blur)

    return filename


def noteshrink_card_from_im(card_im):
    # TODO make this not have to write to file
    tmp_file = write_im(card_im, "tmp.jpg")
    noteshrunk_file = noteshrink_card_from_file(tmp_file)
    noteshrunk_im = cv2.imread(noteshrunk_file, 1)
    os.remove(noteshrunk_file)
    return noteshrunk_im


def noteshrink_card_from_file(card_filename, shrink_max_dim=120):
    img, dpi = noteshrink.load(card_filename)
    img = shrink(img, max_dim=shrink_max_dim)
    options = noteshrink.get_argument_parser(
        # hack to give a required argument from outside sys.argv
        filenames=[card_filename]
    ).parse_args()
    options.num_colors = 2
    options.white_bg = True
    options.quiet = True

    if img is None:
        return

    output_filename = "%s.out.png" % (card_filename)

    samples = noteshrink.sample_pixels(img, options)
    palette = noteshrink.get_palette(samples, options)

    labels = noteshrink.apply_palette(img, palette, options)

    noteshrink.save(output_filename, labels, palette, dpi, options)
    return output_filename


def process_card(card_filename):
    blurred = blur_card(card_filename)
    shrunk_card = noteshrink_card_from_file(blurred)
    # keypoints_card(shrunk_card)
    # TODO return image in correct format
    return


def main():

    for unprocessed_card_file in sys.argv[1:]:
        unprocessed_card = cv2.imread(unprocessed_card_file, 1)
        processed_card = process_card(unprocessed_card_file)
        # TODO cannot currently write bc noteshrink does not return a cv2 image
        # write_im(processed_card, PROCESSED_CARD_FILENAME, PROCESS_CARD_OUT_DIR)


if __name__ == "__main__":
    main()
