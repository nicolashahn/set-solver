#!/usr/bin/env python
"""Test accuracy of card_classifier.py."""

import os
from tqdm import tqdm
from classify_card import classify_card
from card_finder import find_cards, write_cards
from common import SET_GAMES_DIR, SET_GAME_CARDS_DIR, jpgs_in_dir

GAME_NUM = 8
GAME_FILE = os.path.join(SET_GAMES_DIR, 'setgame{}.jpg'.format(GAME_NUM))
LABELED_CARDS_DIR = os.path.join(SET_GAME_CARDS_DIR, 'setgame{}'.format(GAME_NUM))

def test_filenames(card_filenames, expected_labels):
  """Get labels for a list of card filenames, and compare the resulting
  list to the expected label list.
  NOTE: Since this is just comparing two lists of labels, it does not 
  contain information about which card images map to which labels - so
  not a fullproof test, just quick and dirty for development.
  """
  labels = [classify_card(filename) for filename in tqdm(card_filenames)]
  correct = [l for l in labels if l in expected_labels]
  incorrect = [l for l in labels if l not in expected_labels]
  score = float(len(correct)) / float(len(expected_labels))

  print('\nRESULTS\n{} of {} correct, score: {}'.format(
    len(correct), len(expected_labels), score))

  if correct:
    print('\nCorrect:')
    for label in correct:
      print(label)

  if incorrect:
    print('\nIncorrect:')
    for label in incorrect:
      print(label)

  return score

def test_game_accuracy(game_file, labeled_cards_dir):
  """Test one game image file's classify_card accuracy, against a set of
  prelabeled card images from that game file. Must have already run 
  label_all_cards.py on the file and placed them in the appropriate 
  LABELED_CARDS_DIR.
  """
  card_ims = find_cards(game_file)
  card_filenames = write_cards(card_ims)
  expected_labels = jpgs_in_dir(labeled_cards_dir)
  return test_filenames(card_filenames, expected_labels)

def test_cards_in_dir(labeled_cards_dir=LABELED_CARDS_DIR):
  """Feed each card in the directory to card_classifier, and compare
  the outputted label to the actual label, the card's filename
  (card_classifier.py does not use the filename information).
  """
  filenames = jpgs_in_dir(labeled_cards_dir)
  full_paths = [os.path.join(labeled_cards_dir, f) for f in filenames]
  return test_filenames(full_paths, filenames)
  
def main():
  # test_game_accuracy(GAME_FILE, LABELED_CARDS_DIR)
  test_cards_in_dir()

if __name__ == "__main__":
  main()
