#!/usr/bin/env python
"""Classify a SET card image's color, shape, shade, number."""

import os
import sys
import cv2
from extract_shapes import extract_shapes_from_im
from label_all_cards import manually_label_card
from process_card import noteshrink_card_from_im
from common import ALL_SHAPES_DIR, mean, jpgs_in_dir
from vendor.noteshrink import CannotGetPalette


def orb_score(shape_to_find, cv_im, canny=False, min_match_ct=10, thresh_min=100):
    """Use ORB to get a match score for image file shape_to_find and cv_im."""
    img1 = cv2.imread(shape_to_find, 0)
    img2 = cv2.cvtColor(cv_im, cv2.COLOR_BGR2GRAY)

    if canny:
        img1 = cv2.Canny(img1, 100, 200)
        img2 = cv2.Canny(img2, 100, 200)

    orb = cv2.ORB_create()
    orb.setEdgeThreshold(5)

    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    if des2 is None:
        return

    # create BFMatcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    # Match descriptors.
    matches = bf.match(des1, des2)
    # Sort them in the order of their distance.
    matches = sorted(matches, key=lambda x: x.distance)

    ret = sum([m.distance for m in matches[:min_match_ct]])

    return ret


def get_best_orb_matches(card_im, shapes_dir=ALL_SHAPES_DIR, canny=False):
    """Test card image against all shapes in shapes_dir, and return tuples
  (score, label) for the best matches.
  """
    shapes = jpgs_in_dir(shapes_dir)

    segments = extract_shapes_from_im(card_im)
    ret = []

    for segment in segments:
        possibles = []
        for shape in shapes:
            shape_file = os.path.join(shapes_dir, shape)
            score = orb_score(shape_file, segment, canny=canny)
            if score:
                possibles.append((score, shape))

        possibles.sort()
        if possibles:
            ret.append(possibles[0])

    ret.sort()
    return ret


def pixels_mean(pixels):
    """Input is a list of (R,G,B) tuples, output is the average (R,G,B) value."""
    rs = [p[0] for p in pixels]
    gs = [p[1] for p in pixels]
    bs = [p[2] for p in pixels]
    return (mean(rs), mean(gs), mean(bs))


def shape_rgb(card_im):
    """Returns a tuple (R,G,B) of the average value of all non-white pixels
  after noteshrinking (which converts near-white to white).
  """
    shrunk_im = noteshrink_card_from_im(card_im)

    # remove white pixels
    non_whites = []
    for row in shrunk_im:
        for pixel in row:
            if sum(pixel) < 255 * 3:
                non_whites.append(pixel)
    return pixels_mean(non_whites)


def color_diff(rgb1, rgb2):
    """Compute diff in two pixel's colors (R,G,B tuples)."""
    return sum([abs(rgb1[i] - rgb2[i]) for i in range(len(rgb1))])


def classify_color(card_im):
    try:
        unclassified_rgb = shape_rgb(card_im)
    except CannotGetPalette:
        # handled upstream
        return ""

    # precomputed in avg_colors.py
    color_avgs = {"red": (0, 34, 226), "green": (64, 123, 0), "purple": (89, 0, 76)}

    dists = {
        color: color_diff(color_avgs[color], unclassified_rgb) for color in color_avgs
    }

    return min(dists, key=dists.get)


def classify_number_from_shapes(shapes):
    num_shapes = len(shapes)
    return ["", "single", "double", "triple"][num_shapes]


def classify_card_from_im(card_im):
    """Classify the card's attributes, returning a label like
  red-triple-outline-squiggle.jpg."""
    shapes = get_best_orb_matches(card_im, canny=True)
    shades = get_best_orb_matches(card_im)
    color = classify_color(card_im)
    number = classify_number_from_shapes(shapes)

    if any([(not attr) for attr in (shapes, shades, color, number)]):
        print(
            "Could not classify at least one of the attributes of this card. "
            "Please enter the attribute labels manually."
        )
        color, number, shade, shape = manually_label_card(card_im)
    else:
        ret = shapes[0][1]
        _, _, _, shape = ret.split("-")

        ret = shades[0][1]
        _, _, shade, _ = ret.split("-")

    return "-".join([color, number, shade, shape])


def classify_card_from_file(card_file_to_classify):
    card_im = cv2.imread(card_file_to_classify)
    return classify_card_from_im(card_im)


def main():
    card_file_to_classify = sys.argv[1]
    classified_card = classify_card_from_file(card_file_to_classify)
    print(classified_card)


if __name__ == "__main__":
    main()
