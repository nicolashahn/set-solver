#!/usr/bin/env python
"""Classify a SET card image's color, shape, shade, number."""

import os
import sys
import cv2
from diffimg import diff as diff_PIL
from cv2_diff import diff as diff_cv2
from common import ALL_CARDS_LABELED_DIR

def simple_diff(card_file_to_classify, method="PIL"):
  """Diff the given card file against all labeled cards, choose the lowest
  diff valued card. Default diff method is using PIL, can also use cv2.
  """
  scores = {}
  labeled_filenames = [f for f in os.listdir(ALL_CARDS_LABELED_DIR) if f[-4:] == '.jpg']

  # diff against all labeled cards, get best score
  for labeled_filename in labeled_filenames:
    labeled_filename_path = os.path.join(ALL_CARDS_LABELED_DIR, labeled_filename)
    
    # image differentiation algorithm using PIL
    if method == 'PIL':
      scores[labeled_filename] = diff_PIL(
        labeled_filename_path,
        card_file_to_classify,
        delete_diff_file=True
      )

    # using cv2, this method is much slower
    elif method == 'cv2':
      labeled_card = cv2.imread(labeled_filename_path, 1)
      card_to_classify = cv2.imread(card_file_to_classify, 1)
      scores[labeled_filename] = diff_cv2(
        labeled_card,
        card_to_classify
      )

  best = min(scores, key=scores.get)

  # diff score is very bad for all, probably not a card
  if scores[best] > 0.3:
    return None
  return best

def classify_card(card_file_to_classify):
  """Classify the card's attributes."""
  # TODO: more complex methods of classification
  # simple_diff() works okay for shape and number (so far)
  # Okay's suggestion for color: quantization/bucketing
  # Shade: extract shapes as contours, sample the innermost part, greyscale,
  # and diff against a heavily gaussian blurred square of solid/stripes/outline
  # so dark grey, light grey, white
  return simple_diff(card_file_to_classify)

def main():
  card_file_to_classify = sys.argv[1]
  classified_card = classify_card(card_file_to_classify)
  print(classified_card)

if __name__ == "__main__":
  main()
