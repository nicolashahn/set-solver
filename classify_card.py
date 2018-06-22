#!/usr/bin/env python
"""Classify a SET card image's color, shape, shade, number."""

import os
import sys
import cv2
import numpy as np
from extract_shapes import extract_shapes_from_im 
from process_card import noteshrink_card_from_im
from matplotlib import pyplot as plt
from diffimg import diff as diff_PIL
from cv2_diff import diff as diff_cv2
from common import ALL_CARDS_LABELED_DIR, display_im, mean

def classify_simple_diff(card_file_to_classify, method="PIL"):
  """Diff the given card file against all labeled cards, choose the lowest
  diff valued card. Default diff method is using PIL, can also use cv2.
  """
  scores = {}
  labeled_filenames = [f for f in os.listdir(ALL_CARDS_LABELED_DIR) if f[-4:] == '.jpg']

  # diff against all labeled cards, get best score
  for labeled_filename in labeled_filenames:
    labeled_filename_path = os.path.join(ALL_CARDS_LABELED_DIR, labeled_filename)

    # image differentiation algorithm using PIL
    if method == 'PIL':
      scores[labeled_filename] = diff_PIL(
        labeled_filename_path,
        card_file_to_classify,
        delete_diff_file=True
      )

    # using cv2, this method is much slower
    elif method == 'cv2':
      labeled_card = cv2.imread(labeled_filename_path, 1)
      card_to_classify = cv2.imread(card_file_to_classify, 1)
      scores[labeled_filename] = diff_cv2(
        labeled_card,
        card_to_classify
      )

  best = min(scores, key=scores.get)

  # diff score is very bad for all, probably not a card
  if scores[best] > 0.3:
    return None
  return best

def keypoints_card(img):
  THRESH_MIN=100
  flag, thresh = cv2.threshold(img, THRESH_MIN, 255, cv2.THRESH_BINARY)
  # Initiate ORB detector
  orb = cv2.ORB_create()
  # find the keypoints with ORB
  kp,des = orb.detectAndCompute(img,None)
  # compute the descriptors with ORB
  print "KEYPOINTS", len(kp), des
  # draw only keypoints location,not size and orientation
  img2 = cv2.drawKeypoints(img, kp, None, color=(0,255,0), flags=0)

def find_shape(shape_to_find, cv_im):
  MIN_MATCH_COUNT = 10
  THRESH_MIN=100
  img1 = cv2.imread(shape_to_find,0)          # queryImage
  img2 = cv2.cvtColor(cv_im,  cv2.COLOR_BGR2GRAY)

  flag, thresh = cv2.threshold(img2, THRESH_MIN, 255, cv2.THRESH_BINARY)


  orb = cv2.ORB_create()
  orb.setEdgeThreshold(5)

  kp1, des1 = orb.detectAndCompute(img1, None)
  kp2, des2 = orb.detectAndCompute(img2, None)

  if des2 is None:
    return

  # create BFMatcher object
  bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
  # Match descriptors.
  matches = bf.match(des1,des2)
  # Sort them in the order of their distance.
  matches = sorted(matches, key = lambda x:x.distance)

  ret = sum([m.distance for m in matches[:10]])

  return ret

def classify_shape(card_im):
  # change `all-shapes` to `shapes` to go back to using single green cards
  shapes_dir = "image-data/all-shapes"
  shapes = [s for s in os.listdir(shapes_dir) if s[-4:]=='.jpg']

  segments = extract_shapes_from_im(card_im)
  ret = []

  for segment in segments:
    possibles = []
    for shape in shapes:
      shape_file = os.path.join(shapes_dir, shape)
      score = find_shape(shape_file, segment)
      if score:
        possibles.append((score, shape))

    possibles.sort()
    if possibles:
      ret.append(possibles[0])

  ret.sort()
  return ret

def pixels_mean(pixels):
  """Input is a list of (R,G,B) tuples, output is the average (R,G,B) value."""
  rs = [p[0] for p in pixels]
  gs = [p[1] for p in pixels]
  bs = [p[2] for p in pixels]
  return (mean(rs), mean(gs), mean(bs))

def shape_rgb(card_im):
  """Returns a tuple (R,G,B) of the average value of all non-white pixels
  after noteshrinking (which converts near-white to white).
  """
  shrunk_im = noteshrink_card_from_im(card_im)

  # remove white pixels
  non_whites = []
  for row in shrunk_im:
    for pixel in row:
      if sum(pixel) < 255*3:
        non_whites.append(pixel)
  return pixels_mean(non_whites)

def color_diff(rgb1, rgb2):
  """Compute diff in two pixel's colors."""
  return sum([abs(rgb1[i] - rgb2[i]) for i in range(len(rgb1))])

def classify_color(card_im):
  unclassified_rgb = shape_rgb(card_im)

  # precomputed in avg_colors.py
  color_avgs = {
    'red': (0, 34, 226),
    'green': (64, 123, 0),
    'purple': (89, 0, 76)
  }

  dists = {color: color_diff(
    color_avgs[color], unclassified_rgb) for color in color_avgs}

  return min(dists, key=dists.get)

def classify_number(card_im):
  pass

def classify_fill(card_im):
  pass

def classify_card_from_im(card_im):
  shape = classify_shape(card_im)
  color = classify_color(card_im)

  num_shapes = len(shape)

  num_words = [ "", "single", "double", "triple" ][num_shapes]

  if len(shape) > 0:
    ret = shape[0][1]
    _,n,f,s = ret.split("-")

    r = "-".join([color, num_words, f, s ])
    return r

  return ""

def classify_card_from_file(card_file_to_classify):
  """Classify the card's attributes."""
  card_im = cv2.imread(card_file_to_classify)

  return classify_card_from_im(card_im)

def main():
  card_file_to_classify = sys.argv[1]
  classified_card = classify_card(card_file_to_classify)
  print(classified_card)

if __name__ == "__main__":
  main()
