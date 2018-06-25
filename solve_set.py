#!/usr/bin/env python
"""Solve set from a game image, returning the image with the sets indicated."""

import sys
from tqdm import tqdm
from card_finder import find_cards
from classify_card import classify_card_from_im
from classes import Card, SetGame
from common import SOLVE_OUT, write_im, clean_make_dir

def solve_set(game_filename):
  """Given a game image, find the sets in the image, and return the
  SetGame object with the sets indicated on the original image.
  """
  game = SetGame(game_filename)
  card_ims_with_corners = find_cards(game_filename, with_corners=True)
  for im, corner in card_ims_with_corners:
    game.cards.append(Card(im, corner))
  for card in tqdm(game.cards):
    card.label = classify_card_from_im(card.im)
  game.find_sets()
  game.draw_sets()
  return game

def main():
  solved_game = solve_set(sys.argv[1])
  solved_game.print_sets()
  clean_make_dir(SOLVE_OUT)
  write_im(solved_game.im, 'solved.jpg', out_dir=SOLVE_OUT)
  solved_game.display()

if __name__ == "__main__":
  main()
