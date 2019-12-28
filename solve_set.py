#!/usr/bin/env python
"""Solve SET from a game image. Prints the sets found, and optionally
writes and/or displays the game image with the sets indicated.
"""

import argparse
import sys
from SetGame import SetGame
from common import game_img_filename


def get_args():
    parser = argparse.ArgumentParser(description="Solve SET from a game image.")
    parser.add_argument(
        "filename", metavar="filename", type=str, nargs="?", help="Game image filename"
    )
    parser.add_argument(
        "--game",
        dest="game_num",
        type=int,
        help="use a test image from image-data/set-games/setgame<GAME_NUM>.jpg",
    )
    parser.add_argument(
        "--write",
        dest="write",
        action="store_true",
        help="Write the solved image to solve-out/solved.jpg",
    )
    parser.add_argument(
        "--display",
        dest="display",
        action="store_true",
        help="Display the solved image with cv2.display()",
    )
    return parser.parse_args()


def main():
    args = get_args()

    if args.game_num:
        filename = game_img_filename(args.game_num)
    elif args.filename:
        filename = args.filename
    else:
        print("Error: must pass either a filename or --game GAME_NUM")
        sys.exit(1)

    game = SetGame(filename)
    game.solve()
    game.print_sets()
    game.draw_sets()

    if args.write:
        game.write_im("solved.jpg")
    if args.display:
        game.display()


if __name__ == "__main__":
    main()
