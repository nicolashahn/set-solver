#!/usr/bin/env python
"""Common constants/functions shared between modules."""

import os
import shutil
import cv2
import numpy as np


#############
# Constants #
#############

CARD_FINDER_OUT_DIR = "finder-out"
PROCESS_CARD_OUT_DIR = "process-out"
SHAPES_OUT_DIR = "shapes-out"
SOLVE_OUT = "solve-out"

IM_DATA_DIR = "image-data"

# sample images of set games
SET_GAMES_DIR = os.path.join(IM_DATA_DIR, "set-games")

# individual card images from these games cut out and labeled
SET_GAME_CARDS_DIR = os.path.join(IM_DATA_DIR, "set-game-cards")

GAME_FILE_FMT = os.path.join(SET_GAMES_DIR, "setgame{}.jpg")

# all cards labeled
ALL_CARDS_LABELED_DIR = os.path.join(IM_DATA_DIR, "all-cards", "labeled")
ALL_SHAPES_DIR = os.path.join(IM_DATA_DIR, "all-shapes")

# the 4 possible attributes of a card
CARD_ATTRS = {
    "color": ["red", "green", "purple"],
    "number": ["single", "double", "triple"],
    "shade": ["solid", "stripes", "outline"],
    "shape": ["diamond", "squiggle", "capsule"],
}

# size of stored card images
CARD_WIDTH = 450
CARD_HEIGHT = 300


#############
# Functions #
#############


def game_img_filename(n):
    return GAME_FILE_FMT.format(n)


def clean_make_dir(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)


def write_im(im, filename, out_dir=PROCESS_CARD_OUT_DIR, print_path=False):
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    """Write image to given path and filename."""
    out_path = os.path.join(out_dir, filename)
    cv2.imwrite(out_path, im)
    if print_path:
        print(out_path)
    return out_path


def display_im(im, imgname="image", resize=True):
    """Displays image, waits for any key press, then closes windows."""
    # shrink image if huge to fit on screen
    if resize:
        display = shrink(im) if resize else im

    # show image, wait for any key, then close windows
    cv2.imshow(imgname, display)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def jpgs_in_dir(dir):
    return [f for f in os.listdir(dir) if f[-4:] == ".jpg"]


def mean(ns):
    return sum(ns) / (len(ns) or 1)


def median(ns):
    return ns[len(ns) // 2]


def shrink(im, max_dim=1000):
    """Make image a computationally wieldy size if necessary."""
    if len(im.shape) == 3:
        # 'depth' is missing depending on if we're importing original image or not
        height, width, _ = im.shape
    else:
        height, width = im.shape

    ratio = max_dim / float(max(height, width))

    # only resizes if does not fit in max_dim
    if ratio < 1:
        im = cv2.resize(im, (0, 0), fx=ratio, fy=ratio, interpolation=cv2.INTER_AREA)
    return im


def rectify(h, portrait=False):
    """Ensure the 4 points for each card we find have identical ordering."""
    h = h.reshape((4, 2))
    hnew = np.zeros((4, 2), dtype=np.float32)

    # crude auto rotation to put all cards in landscape orientation
    # will not do well with warped perspective, birds-eye only
    xs = [p[0] for p in h]
    ys = [p[1] for p in h]
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)

    # rotates the points based on whether we want portrait or landscape output,
    # and simple check of height > width to determine orientation of original
    correct_orientation = (height > width) if portrait else (not height > width)
    top_l, top_r, bot_r, bot_l = (0, 2, 1, 3) if correct_orientation else (1, 3, 2, 0)

    # point order is clockwise from top left
    add = h.sum(1)
    hnew[top_l] = h[np.argmin(add)]
    hnew[top_r] = h[np.argmax(add)]
    diff = np.diff(h, axis=1)
    hnew[bot_r] = h[np.argmin(diff)]
    hnew[bot_l] = h[np.argmax(diff)]

    return hnew


def scale_points(points, scale):
    """Scale a list of points outwards from the center. `scale` arg can either
  be an float or tuples of floats, for (xscale, yscale).
  """
    if type(scale) == tuple:
        xscale = scale[0]
        yscale = scale[1]
    else:
        xscale = scale
        yscale = scale

    # get center of points
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    midx = max(xs) - ((max(xs) - min(xs)) / 2)
    midy = max(ys) - ((max(ys) - min(ys)) / 2)

    # push points outward
    for point in points:
        x = point[0]
        y = point[1]
        xdist = x - midx
        ydist = y - midy
        newx = midx + xdist * xscale
        newy = midy + ydist * yscale
        point[0] = newx
        point[1] = newy
    return points


def label_to_dict(label):
    """Convert a label like 'red-triple-stripes-squiggle.jpg' to
  {'color':'red', 'number':'triple'...etc}
  """
    tokens = [t.split(".")[0] for t in label.split("-")]
    return dict(zip(sorted(CARD_ATTRS.keys()), tokens))


def keypoints_card(img, thresh_min=100):
    flag, thresh = cv2.threshold(img, thresh_min, 255, cv2.THRESH_BINARY)
    # Initiate ORB detector
    orb = cv2.ORB_create()
    # find the keypoints with ORB
    kp, des = orb.detectAndCompute(img, None)
    # compute the descriptors with ORB
    print("KEYPOINTS", len(kp), des)
    # draw only keypoints location,not size and orientation
    img2 = cv2.drawKeypoints(img, kp, None, color=(0, 255, 0), flags=0)
