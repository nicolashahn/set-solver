#!/usr/bin/env python
"""SetGame class and some helper classes."""

from random import randint
from itertools import combinations
import cv2
from tqdm import tqdm
from common import (
  SOLVE_OUT,
  clean_make_dir,
  display_im,
  write_im,
  label_to_dict
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
    return '<Card {}>'.format(self.label)

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
  def is_set(card1, card2, card3):
    for attr in card1.attrs.keys():
      if len(set([card1.attrs[attr],
                  card2.attrs[attr],
                  card3.attrs[attr]])) == 2:
        return False
    return True

  def find_sets(self):
    """Try all combinations of 3 cards to find sets."""
    combos = combinations(self.cards, 3)
    self.sets = [c for c in combos if self.is_set(*c)]
    return self.sets

  def print_sets(self):
    if not self.sets:
      print '\nNo sets found\n'
    else:
      print '\n{} sets found\n'.format(len(self.sets))
      for i, cards in enumerate(self.sets):
        print 'Set {}:'.format(i+1)
        for card in cards:
          print '  {}'.format(card.label)

  def draw_sets(self):
    """Update original game image with sets highlighted."""
    low = 100
    high = 255
    line_thickness = self.im.shape[0]/100
    for cards in self.sets:
      color = [randint(low,high) for _ in range(3)]
      # so it doesn't end up white or near white
      color[randint(0,2)] = 0
      for card in cards:
        for i in range(-1,len(card.corners)-1):
          p1 = (card.corners[i][0], card.corners[i][1])
          p2 = (card.corners[i+1][0], card.corners[i+1][1])
          cv2.line(self.im, p1, p2, color, line_thickness)

  def write_im(self, filename, out_dir=SOLVE_OUT):
    clean_make_dir(SOLVE_OUT)
    return write_im(self.im, filename, out_dir=SOLVE_OUT)

  def solve(self):
    """Run through entire pipeline to get and save sets."""
    self.get_cards()
    self.find_sets()
