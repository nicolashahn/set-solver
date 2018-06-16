#!/usr/bin/env python
"""Common constants/functions shared between modules."""

import os
import cv2

# Constants

CARD_FINDER_OUT_DIR = 'finder-out'
PROCESS_CARD_OUT_DIR = 'process-out'

IM_DATA_DIR = 'image-data'

# individual labeled card images
LABELED_DIR = os.path.join(IM_DATA_DIR, 'all-cards', 'labeled')

# the 4 possible attributes of a card
CARD_ATTRS = {
  'color': ['red', 'green', 'purple'],
  'number': ['single', 'double', 'triple'],
  'shade': ['solid', 'stripes', 'outline'],
  'shape': ['diamond', 'squiggle', 'capsule']
}

# Functions

def write_im(card,
             filename,
             out_dir=PROCESS_CARD_OUT_DIR,
             print_path=False):
  """Write image to given path and filename."""
  out_path = os.path.join(out_dir, filename)
  cv2.imwrite(out_path, card)
  if print_path:
    print(out_path)

def display_im(im, imgname='image', resize=True):
  """Displays image, waits for any key press, then closes windows."""
  # shrink image if huge to fit on screen
  if resize:
    display = shrink(im) if resize else im

  # show image, wait for any key, then close windows
  cv2.imshow(imgname, display)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

def mean(ns):
  return sum(ns)/(len(ns) or 1)

def median(ns):
  return ns[len(ns)/2]

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
    im = cv2.resize(im, (0,0), fx=ratio, fy=ratio)
  return im
