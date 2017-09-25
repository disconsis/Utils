#!/usr/bin/python3

from PIL import Image
from math import ceil
from random import shuffle
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('input_file')
parser.add_argument('output_file')
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('-nr', '--norand', action='store_true',
                    help='Outputs the same colours every time')
args = parser.parse_args()

INPUT_IMG = args.input_file
DISTINCT_IMG = args.output_file

if args.verbose:
    print("Processing {}".format(INPUT_IMG))
img = Image.open(INPUT_IMG)
new_img = Image.new('RGB', img.size)

if args.verbose:
    print("Finding colours")
col_set = set()
for x in range(img.size[0]):
    for y in range(img.size[1]):
        col = img.getpixel((x, y))
        col_set.add(col)
if args.verbose:
    print("Found {} colours in the image".format(len(col_set)))
else:
    print("{} colours".format(len(col_set)))

if args.verbose:
    print("Making colours more distinct")
col_list = list(col_set)
if not args.norand:
    shuffle(col_list)
col_per = int(ceil(len(col_list)/3))
col_rate = int(255/col_per)
col_dict = dict()
for idx_per in range(1, col_per + 1):
    empty = False
    for i in range(3):
        if not len(col_list):
            empty = True
            break
        col_old = col_list.pop()
        col_new = [0, 0, 0]
        col_new[i] = col_rate * idx_per
        col_dict[col_old] = tuple(col_new)
    if empty:
        break

if args.verbose:
    print("Replacing colours")
for x in range(img.size[0]):
    for y in range(img.size[1]):
        col_old = img.getpixel((x, y))
        col_new = col_dict[col_old]
        new_img.putpixel((x, y), col_new)

if args.verbose:
    print("Saving processed image as {}".format(DISTINCT_IMG))
new_img.save(DISTINCT_IMG)
