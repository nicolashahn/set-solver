#!/usr/bin/env python
"""Test accuracy of card_classifier.py."""

import os
from tqdm import tqdm
from classify_card import classify_card
from card_finder import find_cards, write_cards
from common import SET_GAMES_DIR, SET_GAME_CARDS_DIR

GAME_NUM = 8
GAME_FILE = os.path.join(SET_GAMES_DIR, 'setgame{}.jpg'.format(GAME_NUM))
LABELED_CARDS_DIR = os.path.join(SET_GAME_CARDS_DIR, 'setgame{}'.format(GAME_NUM))

def test_game_accuracy(game_file, labeled_cards_dir):
  """Test one game image file's classify_card accuracy, against a set of
  prelabeled card images from that game file. Must have already run 
  label_all_cards.py on the file and placed them in the appropriate 
  LABELED_CARDS_DIR.
  """
  card_ims = find_cards(game_file)
  card_filenames = write_cards(card_ims)
  labels = [classify_card(filename) for filename in tqdm(card_filenames)]
  expected = os.listdir(LABELED_CARDS_DIR)
  correct = [l for l in labels if l in expected]
  incorrect = [l for l in labels if l not in expected]
  score = float(len(correct)) / float(len(expected))

  print('\nRESULTS\n{} of {} correct, score: {}\n'.format(
    len(correct), len(expected), score))
  print('Incorrect:')
  for label in incorrect:
    print(label)
  return score

def test_cards_in_dir(labeled_cards_dir=LABELED_CARDS_DIR):
  """Feed each card in the directory to card_classifier, and compare
  the outputted label to the actual label in the card's filename.
  """
  # TODO
  pass
  
def main():
  test_game_accuracy(GAME_FILE, LABELED_CARDS_DIR)

if __name__ == "__main__":
  main()
