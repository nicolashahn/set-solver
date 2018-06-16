# set-solver
Solve the SET card game using OpenCV

## Setup

\#TODO

## Files

* `card_finder.py` - given a game image, outputs images of all cards found.
* `label_all_cards.py` - single use script to easily label cards.
* `classify_card.py` - given a card image, outputs the best guess of what card it is.
* `test.py` - tests are life
* `common.py` - common constants or functions shared between scripts
* `cv2_diff.py` - the same functionality as [diffimg](https://github.com/nicolashahn/diffimg), but implemented using `cv2` instead of `PIL`. Gives different ratios and I still need to investigate why. Also runs way slower.
* `image-data` - all image data, including raw game images, labeled card images

## Tasks

- [ ] Increase card classification accuracy
  - [ ] Bucket colors - https://mzucker.github.io/2016/09/20/noteshrink.html
    - [ ] Generate bucketed+labeled card set
    - [ ] Bucket colors in the unclassified card before comparing against the bucketed+labeled cards
  - [ ] Find a reliable way to choose shade (solid/stripes/outline)
  - [ ] "Shove a neural net into it" - optional if OpenCV isn't enough
    - [ ] I don't want to take hundreds of pictures of cards, so maybe fake a training set? Take the same image and artificially introduce jitter in a variety of ways (position, skew, rotation, white balance, lighting, etc) that mimics the real differences we'd get
- [ ] Solve SET once the image's card's labels are in memory
   - [ ] Brute force it first
   - [ ] Better than brute force? Might be interesting to think about if SET's # cards on table, # attributes, # categories per attribute were increased
- [ ] Get the pipeline smoothed out. Input is a game image, output is the sets overlayed
  - [ ] Write outlines of sets onto original image
  - [ ] E2E test for entire pipeline
  - [ ] More tests in general
- [ ] Make it run on a phone
  - [ ] React Native app that sends an image to a Flask app?
  - [ ] Have the whole pipeline run on the phone? Going to require an entire rewrite of the pipeline
