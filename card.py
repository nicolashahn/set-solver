"""Find SET cards in an image."""

import cv2
import numpy as np

# in a game there's usually 12, but 15 max if no sets in the 12
MAXCARDS = 15

IMG_FILENAME_TEMPLATE = 'image-data/set-games/setgame{}.jpg'

OUT_WIDTH = 450
OUT_HEIGHT = 300

def game_img_filename(n):
  return IMG_FILENAME_TEMPLATE.format(n)

def display(im, imgname='image'):
  """Displays image, waits for any key press, then closes windows."""
  cv2.imshow(imgname, im)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

def shrink(im, max_dim=1000):
  """Make image a computationally wieldy size if necessary."""
  # 'depth' is missing depending on if we're importing original image or not
  if len(im.shape) == 3:
    height, width, _ = im.shape
  else:
    height, width = im.shape

  ratio = max_dim / float(max(height, width))
  if ratio < 1:
    im = cv2.resize(im, (0,0), fx=ratio, fy=ratio)
  return im

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
  if height < width:
    top_l, top_r, bot_r, bot_l = 0,2,1,3
  else:
    top_l, top_r, bot_r, bot_l = 1,3,2,0

  add = h.sum(1)
  hnew[top_l] = h[np.argmin(add)]
  hnew[top_r] = h[np.argmax(add)]
  diff = np.diff(h,axis = 1)
  hnew[bot_r] = h[np.argmin(diff)]
  hnew[bot_l] = h[np.argmax(diff)]

  return hnew

def find_cards(filename,
               resize=False,
               out_w=OUT_WIDTH,
               out_h=OUT_HEIGHT):
  """Find SET game cards in image."""

  # 1 = color, 0 = gray, -1 = color+alpha
  orig_im = cv2.imread(filename, 1)
  im = cv2.imread(filename, 0)

  # shrink image if huge
  if resize:
    im = shrink(im)
    orig_im = shrink(orig_im)

  # filters to make it easier for opencv to find card
  blur = cv2.GaussianBlur(im,(3,3),1000)

  # this '180' might need to be tweaked based on histogram of image
  flag, thresh = cv2.threshold(blur, 180, 255, cv2.THRESH_BINARY)

  # `image` is the thrown away value
  _, contours, hierarchy = cv2.findContours(
    thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
  # takes the $MAXCARDS largest contours
  contours = sorted(contours, key=cv2.contourArea,reverse=True)

  # will likely never have < 15 contours unless image is pure black or something
  for i in range(min(MAXCARDS, len(contours))):
    card = contours[i]
    peri = cv2.arcLength(card,True)
    approx = cv2.approxPolyDP(card,0.1*peri,True)

    # quadrangles only
    if len(approx) == 4: 

      # try to order each of the 4 points correctly
      approx = rectify(approx)

      # create an image of just the card
      h = np.array([ 
        [0,0],
        [out_w-1,0],
        [out_w-1,out_h-1],
        [0,out_h-1]
      ],np.float32)
      transform = cv2.getPerspectiveTransform(approx,h)
      warp = cv2.warpPerspective(orig_im,transform,(out_w,out_h))
      yield warp

def main():
  # for filename in [game_img_filename(i) for i in range(7)]:
    # find_cards(filename)
  cards = find_cards(game_img_filename(3))
  [display(card) for card in cards]

if __name__ == '__main__':
  main()
