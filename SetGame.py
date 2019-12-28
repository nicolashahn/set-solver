#!/usr/bin/env python
"""SetGame class and some helper classes."""

from random import randint, shuffle
from itertools import permutations, combinations
import cv2
import numpy as np
from tqdm import tqdm
from common import (
    SOLVE_OUT,
    clean_make_dir,
    display_im,
    write_im,
    label_to_dict,
    scale_points,
)
from classify_card import classify_card_from_im
from card_finder import find_cards


class Cv2Image(object):
    def display(self):
        display_im(self.im)


class Card(Cv2Image):
    def __init__(self, im, corners):
        self.im = im
        # list of (x,y) tuples mapping to the corners of the card in original im
        self.corners = corners
        self.label = None

    def __repr__(self):
        return "<Card {}>".format(self.label)

    @property
    def attrs(self):
        if self.label:
            return label_to_dict(self.label)


class SetGame(Cv2Image):
    def __init__(self, filename):
        self.filename = filename
        self.im = cv2.imread(filename, 1)
        self.cards = []
        # list of Card 3-tuples
        self.sets = []

    def get_cards(self, show_tqdm=True):
        """Find and classify cards from game image."""
        card_ims_with_corners = find_cards(self.filename, with_corners=True)
        for im, corner in card_ims_with_corners:
            self.cards.append(Card(im, corner))
        card_iter = tqdm(self.cards) if show_tqdm else self.cards
        for card in card_iter:
            card.label = classify_card_from_im(card.im)

    @staticmethod
    def is_set(cards):
        for attr in cards[0].attrs.keys():
            if len(set([card.attrs[attr] for card in cards])) == 2:
                return False
        return True

    def find_sets(self):
        """Try all combinations of 3 cards to find sets."""
        combos = combinations(self.cards, 3)
        self.sets = [c for c in combos if self.is_set(c)]
        return self.sets

    def print_sets(self):
        if not self.sets:
            print("\nNo sets found\n")
        else:
            print("\n{} sets found\n".format(len(self.sets)))
            for i, cards in enumerate(self.sets):
                print("Set {}:".format(i + 1))
                for card in cards:
                    print("  {}".format(card.label.split(".")[0]))

    def draw_sets(self):
        """Update original game image with sets highlighted."""
        # base line thickness (thins for each additional box)
        base_thickness = self.im.shape[0] / 100
        # how many boxes are around each card
        card_boxes = {card: 0 for card in self.cards}

        colors = list(
            set(
                list(permutations([102, 102, 230]))
                + list(permutations([102, 178, 230]))
            )
        )
        shuffle(colors)
        for i, cards in enumerate(self.sets):
            # generate a random color for each set's boxes
            color = colors[i]

            for card in cards:
                # make box bigger if card already has box(es)
                xscale = card_boxes[card] * 0.08 + 1.0
                yscale = card_boxes[card] * 0.12 + 1.0
                line_thickness = int(
                    base_thickness - card_boxes[card] * (base_thickness / 10)
                )
                card_boxes[card] += 1
                corners = scale_points(np.copy(card.corners), (xscale, yscale))

                for pt in range(-1, len(card.corners) - 1):
                    p1 = (corners[pt][0], corners[pt][1])
                    p2 = (corners[pt + 1][0], corners[pt + 1][1])
                    cv2.line(self.im, p1, p2, color, line_thickness)

    def write_im(self, filename, out_dir=SOLVE_OUT):
        if out_dir == SOLVE_OUT:
            clean_make_dir(out_dir)
        return write_im(self.im, filename, out_dir=out_dir)

    def solve(self):
        """Run through entire pipeline to get and save sets."""
        self.get_cards()
        self.find_sets()
