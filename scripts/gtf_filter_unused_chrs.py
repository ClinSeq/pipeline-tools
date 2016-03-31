#!/usr/bin/env python

import sys

## script to retain comment lines and genes on chrs 1-22,X,Y,MT from a GTF file
## usage: cat file.gtf|python cleanGtf.py > cleaned.gtf

for line in sys.stdin:
    items = line.split("\t")
    if [ items[0] in range(1,23) + ['X', 'Y', 'MT'] ] or line.startswith("#"):
	sys.stdout.write("\t".join(items))

# range(1,23) + ['X', 'Y', 'MT'] gives a list 1-22, X, Y, MT
