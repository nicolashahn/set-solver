#!/usr/bin/env python
"""`diffimg` implemented using cv2 instead of PIL. Unfortunately this
method appears to be much slower - will have to investigate why.
"""

import cv2
import diffimg
from common import display_im

def diff(im1, im2, display=False):
  """Diff cv2 images. Returns a ratio."""
  diff_im = cv2.subtract(im1, im2)
  channels_total = sum([sum([sum(x) for x in y]) for y in diff_im])
  num_channel_values = len(diff_im) * len(diff_im[0]) * 3 * 255
  if display:
    display_im(diff_im)
  return float(channels_total) / float(num_channel_values)

def main():
  """Classify a card in the /out folder, need to run
  `./find_cards.py <file> --write` first. Just compares a labeled and 
  non-labeled card file, both picked at random.
  """
  im1_f = 'out/card11.jpg'
  im2_f = 'image-data/all-cards/labeled/red-double-solid-diamond.jpg'
  im1 = cv2.imread(im1_f)
  im2 = cv2.imread(im2_f)
  ratio = diff(im1, im2)
  print "cv2 ratio:", ratio
  print "PIL ratio:", diffimg.diff(im1_f, im2_f)

if __name__ == "__main__":
  main()
