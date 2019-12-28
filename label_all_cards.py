#!/usr/bin/env python
"""Open images with SET cards, find the cards in the image, and allow
the user to label them manually, then save the image with a filename
that signifies the card's attributes. Meant to be used only once to
generate a set of all card images.
"""

import os
import cv2
import card_finder
from common import CARD_ATTRS

IN_FILENAMES = """
  image-data/set-games/setgame5.jpg
""".split()

OUT_DIR = "image-data/set-game-cards/setgame5"


def get_attr_label(card, attr):
    """
    Prompt the user to classify the card's attribute by showing the card image and
    asking for keyboard input.
    """
    # show user the options
    prompt = "Enter the card's {}:\n".format(attr.upper())
    for i, option in enumerate(CARD_ATTRS[attr]):
        prompt += "  For {}, enter '{}'\n".format(option.upper(), i + 1)
    prompt += "If not a card, enter 'n': "
    print(prompt)

    # show the card, handle input
    cv2.imshow("card", card)
    key = chr(cv2.waitKey(0))
    if "n" in key:
        cv2.destroyAllWindows()
        return
    return CARD_ATTRS[attr][int(key) - 1]


def manually_label_card(card):
    """
    Display a card to the user, who can then label the:
      - color: red, green, purple
      - number: single, double, triple
      - shade: solid, stripes, outline
      - shape: diamond, squiggle, capsule
    Returns a list of the chosen attrs (as strs) in the order shown above.
    """
    print(
        "Select the window with the card image when entering keys. "
        "Keys entered here will not be registered."
    )
    tokens = []
    for attr in sorted(CARD_ATTRS.keys()):
        choice = get_attr_label(card, attr)
        print("You picked {}".format(choice.upper()))
        tokens.append(choice)

    # give opportunity to fix mistakes
    print(
        "Your choices: {}\nIf this is wrong, enter 'n', otherwise "
        "any other key".format(tokens)
    )
    key = chr(cv2.waitKey(0))
    cv2.destroyAllWindows()
    if "n" in key:
        tokens = manually_label_card(card)
    return tokens


def label_and_save(card):
    """
    Prompt the user to label the card and then save to a filename like:
    <color>-<number>-<shade>-<shape>.jpg
    Example:
    green-double-outline-capsule.jpg
    """
    attrs = manually_label_card(card)
    filename = os.path.join(OUT_DIR, "-".join(attrs) + ".jpg")
    print("Writing {}".format(filename))
    cv2.imwrite(filename, card)


def main():
    """For each of the given filenames, show each card found and allow the
  user to label the file, then save it in the output directory.
  """
    for filename in IN_FILENAMES:
        cards = card_finder.find_cards(filename)
        for card in cards:
            label_and_save(card)


if __name__ == "__main__":
    main()
