#!/usr/bin/env python

"""slopIntervalList.py

Script to slop interval_list file by SLOP bases (hard coded).

usage: cat file.interval_list | python slopIntervalList.py > slopped.interval_list

This script does not merge overlapping intervals after slopping. 

""" 

import sys

SLOP = 20

for line in sys.stdin:
    items = line.split("\t")
    # if we're not reading the header
    if not items[0].startswith("@") and len(items) > 2:
        items[1] = str(int(items[1]) - SLOP)
        items[2] = str(int(items[2]) + SLOP)
        
    sys.stdout.write("\t".join(items))

