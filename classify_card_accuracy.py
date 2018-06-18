#!/usr/bin/env python
"""Test accuracy of card_classifier.py. To use this, generate labeled
card images with label_all_cards.py to a directory and pass the directory
to test_cards_in_dir()."""

import os
from tqdm import tqdm
from classify_card import classify_card
from card_finder import find_cards, write_cards
from common import SET_GAMES_DIR, SET_GAME_CARDS_DIR, jpgs_in_dir

GAME_NUM = 8
GAME_FILE = os.path.join(SET_GAMES_DIR, 'setgame{}.jpg'.format(GAME_NUM))
LABELED_CARDS_DIR = os.path.join(SET_GAME_CARDS_DIR, 'setgame{}'.format(GAME_NUM))

def get_score(correct, incorrect):
  total_count = len(correct) + len(incorrect)
  score = float(len(correct)) / float(total_count)

  print('\nRESULTS\n{} of {} correct, score: {}'.format(
    len(correct), total_count, score))

  if correct:
    print('\nCorrect:')
    for label in correct:
      print(label)

  if incorrect:
    print('\nIncorrect:')
    for label in incorrect:
      print(label)

  return score

def test_cards_in_dir(labeled_cards_dir=LABELED_CARDS_DIR):
  """Feed each card in the directory to card_classifier, and compare
  the outputted label to the actual label, the card's filename
  (card_classifier.py does not use the filename information).
  """
  correct, incorrect = [], []
  filenames = jpgs_in_dir(labeled_cards_dir)
  for filename in tqdm(filenames):
    full_path = os.path.join(labeled_cards_dir, filename)
    if classify_card(full_path) == filename:
      correct.append(filename)
    else:
      incorrect.append(filename)
  return get_score(correct, incorrect)
  
def main():
  test_cards_in_dir()

if __name__ == "__main__":
  main()
