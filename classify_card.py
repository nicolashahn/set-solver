#!/usr/bin/env python
"""Classify a SET card image's color, shape, shade, number."""

import os
import sys
import cv2
from diffimg import diff
from common import LABELED_DIR, CARD_ATTRS

def simple_diff(card_file_to_classify):
  """Diff the given card file against all labeled cards, choose the lowest
  diff valued card.
  """
  scores = {}
  labeled_filenames = [f for f in os.listdir(LABELED_DIR) if f[-4:] == '.jpg']

  # diff against all labeled cards, get best score
  for labeled_filename in labeled_filenames:
    labeled_filename_path = os.path.join(LABELED_DIR, labeled_filename)
    scores[labeled_filename] = diff(
      labeled_filename_path,
      card_file_to_classify,
      delete_diff_file=True
    )
  best = min(scores, key=scores.get)

  # diff score is very bad for all, probably not a card
  if scores[best] > 0.25:
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
