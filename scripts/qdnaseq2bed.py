#!/usr/bin/env python

__author__ = 'dankle'

import argparse
import sys

usage = """
Convert QDNAseq output to BED
USAGE: python qdnaseq2bed.py -i qdnaseq.txt
"""
ap = argparse.ArgumentParser()
ap.add_argument('-i', help="fasta file", action="store")
ap.add_argument('-n', help="name of the column to select (default=segmented)", default="segmented")
opts = ap.parse_args()

if opts.i is None:
    print( usage )
    ap.print_help()
    sys.exit(1)

chr_index = 0
start_index = 1
end_index = 2
segmented_index = -1

input_file = open(opts.i)
for i, line in enumerate(input_file):
    # header line starts with "chromosome", skip it
    if line.startswith("chromosome"):
	elements = line.split("\t")
	segmented_index = elements.index(opts.n)
	continue

    # split line
    elements = line.split("\t")

    # convert scientific notation to int
    start = int(float(elements[1]))
    end = int(float(elements[2]))

    # write result if value != NA
    if elements[segmented_index] != "NA":
	sys.stdout.write(
	    elements[0] + "\t" +
	    str(start) + "\t" +
	    str(end) + "\t" +
	    "bin" + str(i) + "\t" +
	    elements[segmented_index] + "\n"
	)
input_file.close()
