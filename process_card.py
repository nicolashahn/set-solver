#!/usr/bin/env python
"""Process a card image to make it easier to match an unlabeled card to
the correct labeled card."""

import os
import sys
import cv2
from common import PROCESS_CARD_OUT_DIR, write_im

PROCESSED_CARD_FILENAME = 'processed.jpg'

def process_card(card_im):
  """Process a card: #TODO for what this means, but probably at least
  bucketing colors.
  """
  # TODO
  return card_im

def main():
  unprocessed_card_file = sys.argv[1]
  unprocessed_card = cv2.imread(unprocessed_card_file, 1)
  processed_card = process_card(unprocessed_card)
  write_im(processed_card, PROCESSED_CARD_FILENAME, PROCESS_CARD_OUT_DIR)

if __name__ == "__main__":
  main()
