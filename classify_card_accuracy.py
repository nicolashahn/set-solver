#!/usr/bin/env python
"""Test accuracy of card_classifier.py. To use this, generate labeled
card images with label_all_cards.py to a directory and pass the directory
to test_cards_in_dir()."""

import os
from tqdm import tqdm
from classify_card import classify_card_from_file
from card_finder import find_cards, write_cards
from common import (
    SET_GAMES_DIR,
    SET_GAME_CARDS_DIR,
    CARD_ATTRS,
    jpgs_in_dir,
    label_to_dict,
)

GAME_NUM = 8
GAME_FILE = os.path.join(SET_GAMES_DIR, "setgame{}.jpg".format(GAME_NUM))
LABELED_CARDS_DIR = os.path.join(SET_GAME_CARDS_DIR, "setgame{}".format(GAME_NUM))


def get_score(fle_tuples):
    scores = {key: 0 for key in sorted(CARD_ATTRS.keys())}
    perfect_classifications = 0
    incorrect = []
    for filename, label, expected in fle_tuples:
        for key in sorted(label.keys()):
            if label[key] == expected[key]:
                scores[key] += 1
            else:
                print(filename, "EXPECTED", expected[key], "BUT GOT", label[key])
        if label == expected:
            perfect_classifications += 1
        else:
            incorrect.append(filename)
    if incorrect:
        print("Incorrectly labeled:")
        for filename in incorrect:
            print(filename)

    total_score = 0
    for key in sorted(scores.keys()):
        score = scores[key]
        possible = len(fle_tuples)

        print("Score for {}: {} / {}".format(key, score, possible))
        total_score += score

    total_possible = 4 * len(fle_tuples)
    overall_accuracy = float(total_score) / float(total_possible)
    print("Overall accuracy: {}%".format(overall_accuracy * 100))

    perfect_accuracy = 100 * float(perfect_classifications) / len(fle_tuples)
    print(
        "Perfect (full card) classifications: {} / {} - {}%".format(
            perfect_classifications, len(fle_tuples), perfect_accuracy
        )
    )

    return overall_accuracy


def test_cards_in_dir(labeled_cards_dir=LABELED_CARDS_DIR):
    """Feed each card in the directory to card_classifier, and compare
  the outputted label to the actual label, the card's filename
  (card_classifier.py does not use the filename information).
  """
    fle_tuples = []
    filenames = jpgs_in_dir(labeled_cards_dir)

    for filename in tqdm(filenames):
        full_path = os.path.join(labeled_cards_dir, filename)
        label = classify_card_from_file(full_path)
        label_dict = label_to_dict(label)
        expected_dict = label_to_dict(filename)
        fle_tuples.append((filename, label_dict, expected_dict))

    return fle_tuples


def main():
    all_runs = []
    for game_num in [4, 5, 7, 8, 10, 11]:
        print("")
        labeled_card_dir = os.path.join(
            SET_GAME_CARDS_DIR, "setgame{}".format(game_num)
        )
        this_run = test_cards_in_dir(labeled_card_dir)
        print("SCORE FOR GAME {}".format(game_num))
        get_score(this_run)

        all_runs.extend(this_run)

    print("-" * 20)
    print("FULL SCORE")
    get_score(all_runs)


if __name__ == "__main__":
    main()
