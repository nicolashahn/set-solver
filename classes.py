#!/usr/bin/env python
"""SET card game, card, shape represented as classes."""

from random import randint
from itertools import combinations
import cv2
from common import display_im, label_to_dict


class Cv2Image(object):

  def display(self):
    display_im(self.im)


class Card(Cv2Image):

  def __init__(self,
               im,
               corners,
               label=None,
               game_im_filename=None):
    self.im = im
    self.game_im_filename = game_im_filename
    # list of (x,y) tuples mapping to the corners of the card in original im
    self.corners = corners
    # list of Shape objects
    self.label = label

  def __repr__(self):
    return '<Card label: {}>'.format(self.label)

  @property
  def attrs(self):
    if self.label:
      return label_to_dict(self.label)


class SetGame(Cv2Image):

  def __init__(self, filename, cards=[]):
    self.filename = filename
    self.im = cv2.imread(filename, 1)
    self.cards = cards
    # list of Card 3-tuples
    self.sets = []

  @staticmethod
  def is_set(card1, card2, card3):
    for attr in card1.attrs.keys():
      if len(set([card1.attrs[attr],
                  card2.attrs[attr],
                  card3.attrs[attr]])) == 2:
        return False
    return True

  def find_sets(self):
    combos = combinations(self.cards, 3)
    self.sets = [c for c in combos if self.is_set(*c)]
    return self.sets

  def draw_sets(self):
    """Update original game image with sets highlighted."""
    for cards in self.sets:
      color = (randint(0,255), randint(0,255), randint(0,255))
      for card in cards:
        for p in card.corners:
          cv2.circle(self.im, (p[0], p[1]), 0, color, self.im.shape[0]/100)
