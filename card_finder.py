#!/usr/bin/env python
"""Find SET cards in an image.
Overall process is more or less this:
http://arnab.org/blog/so-i-suck-24-automating-card-games-using-opencv-and-python
"""

import argparse
import os
import shutil
import sys
import cv2
import numpy as np
from common import (
  CARD_FINDER_OUT_DIR,
  display_im,
  mean,
  median,
  shrink
)

# technically there's a possibility of 18 cards required:
# https://norvig.com/SET.html
# but we'll simplify the problem for now
MAXCARDS = 15

GAME_FILE_FMT = 'image-data/set-games/setgame{}.jpg'
OUT_FILE_FMT = 'card{}.jpg'

# output set card image dimensions
OUT_WIDTH = 450
OUT_HEIGHT = 300

# min channel cutoff for the threshold filter
THRESH_MIN = 180
# how much a contour's area can differ from the mean of the top MAXCARDS
CONTOUR_AREA_TOLERANCE = 2.0

def game_img_filename(n):
  return GAME_FILE_FMT.format(n)

def remove_contour_outliers(contours):
  """Remove contours that differ greatly from the median size.
  If most of the top contours are cards, this gets rid of overly large
  or small polygons that are likely not cards.
  """
  # get median of largest contour areas
  med = median([cv2.contourArea(contours[i]) for i in range(MAXCARDS)])

  def area_filter(c, tolerance=CONTOUR_AREA_TOLERANCE):
    """Remove this contour if area is too far from the median."""
    c_area = cv2.contourArea(c)
    return ((1/tolerance)*med < c_area) and (c_area < tolerance*med)

  contours = filter(area_filter, contours)
  return contours
  
def rectify(h):
  """Ensure the 4 points for each card we find have identical ordering."""
  h = h.reshape((4,2))
  hnew = np.zeros((4,2),dtype = np.float32)

  # crude auto rotation to put all cards in landscape orientation
  # will not do well with warped perspective, birds-eye only
  xs = [p[0] for p in h]
  ys = [p[1] for p in h]
  width = max(xs) - min(xs)
  height = max(ys) - min(ys)
  top_l, top_r, bot_r, bot_l = (0,2,1,3) if height < width else (1,3,2,0)

  # point order is clockwise from top left
  add = h.sum(1)
  hnew[top_l] = h[np.argmin(add)]
  hnew[top_r] = h[np.argmax(add)]
  diff = np.diff(h,axis = 1)
  hnew[bot_r] = h[np.argmin(diff)]
  hnew[bot_l] = h[np.argmax(diff)]

  return hnew

def find_cards(filename,
               out_w=OUT_WIDTH,
               out_h=OUT_HEIGHT,
               display_points=False):
  """Find SET game cards in image and return as a list of images."""
  # 1 = color, 0 = gray, -1 = color+alpha
  orig_im = cv2.imread(filename, 1)
  im = cv2.imread(filename, 0)

  # this may be useful later
  # avg_brightness = mean([mean(row) for row in im])

  # filters to make it easier for opencv to find card
  blur = cv2.GaussianBlur(im,(1,1),1000)

  flag, thresh = cv2.threshold(blur, THRESH_MIN, 255, cv2.THRESH_BINARY)

  # `image` is the thrown away value
  _, contours, hierarchy = cv2.findContours(
    thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

  # sort contours by largest volume
  contours = sorted(contours, key=cv2.contourArea,reverse=True)

  # throw out contours that are far from the median size
  contours = remove_contour_outliers(contours)

  # will likely never have < MAXCARDS contours (unless solid black or similar)
  for i in range(min(MAXCARDS, len(contours))):
    card = contours[i]
    peri = cv2.arcLength(card,True)
    approx = cv2.approxPolyDP(card,0.1*peri,True)

    # quadrangles only
    if len(approx) == 4:

      # order each of the 4 points uniformly, rotating if necessary
      approx = rectify(approx)

      if display_points:
        display_im(approx)
        for point in approx:
          cv2.circle(orig_im, (point[0], point[1]), 0, (0,0,255), im.shape[0]/100)

      # create an image of just the card
      h = np.array([ 
        [0,0],
        [out_w-1,0],
        [out_w-1,out_h-1],
        [0,out_h-1]
      ],np.float32)
      transform = cv2.getPerspectiveTransform(approx,h)
      warp = cv2.warpPerspective(orig_im,transform,(out_w,out_h))
      if not display_points:
        yield warp

  if display_points:
    display_im(orig_im)

def write_cards(cards, out_dir=CARD_FINDER_OUT_DIR, out_file=OUT_FILE_FMT):
  """Write enumerated card image files, print filenames."""
  # clear old cards from dir
  if os.path.exists(out_dir):
    shutil.rmtree(out_dir)
  os.mkdir(out_dir)

  # write each card, numbered
  for i, card in enumerate(cards):
    out_path = os.path.join(out_dir, out_file.format(str(i).zfill(2)))
    cv2.imwrite(out_path, card)
    print(out_path)

def make_parser():
  """Argument parser
  game_file:    image with up to MAXCARDS set cards
  write:        write output images to files
  display:      show images using cv2.imshow()
  """
  parser = argparse.ArgumentParser(description='Find SET cards in an image.')
  parser.add_argument('game_num', metavar='game_num', type=int)
  parser.add_argument('--write', dest='write', action='store_true')
  parser.add_argument('--display', dest='display', action='store_false')
  return parser.parse_args()

def main():
  """Find cards, then either write to files or display images.
  Displaying images is the default behavior.
  """
  args = make_parser()
  img_file = game_img_filename(args.game_num)
  cards = find_cards(img_file)
  if args.write:
    write_cards(cards)
  if args.display:
    [display_im(card) for card in cards]

if __name__ == '__main__':
  main()
