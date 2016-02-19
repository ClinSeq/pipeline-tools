#!/usr/bin/env python

__author__ = 'dankle'


import argparse
import sys
import os
import re

usage = """
Simple slice of a whole chromosome from an interval list
USAGE: python grepIntervalList.py -i myfile.interval_list -s "chr17"
"""
ap = argparse.ArgumentParser()
ap.add_argument('-i', help="interval_list file", action="store")
ap.add_argument('-c', help="string to grep", action="store")

opts = ap.parse_args()
interval_list_file = opts.i
chromosome = opts.c

if interval_list_file is None or chromosome is None:
    print( usage )
    ap.print_help()
    sys.exit(1)

intervals = open(interval_list_file )

for i, line in enumerate(intervals):
    if line.startswith("@"):
        if line.startswith("@SQ"):
            # print only @SQ lines matching the specified chromosome
            elements = line.split("\t")
            if elements[1] == "SN:" + chromosome:
                sys.stdout.write(line)
        else:
            sys.stdout.write(line)
    else:
        elements = line.split("\t")
        ## chr is the first element, if it matches then print entire line
        if elements[0] == chromosome:
            sys.stdout.write(line)

