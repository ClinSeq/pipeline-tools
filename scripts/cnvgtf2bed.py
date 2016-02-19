#!/usr/bin/env python

__author__ = 'dankle'

import argparse
import sys

usage = """
Converts a GTF file with an additional numeric column to bed format.
Useful to convert "CNV-GTF" to BED
USAGE: python cnvgtf2bed.py -i myfile.fasta -n gene_id
"""
ap = argparse.ArgumentParser()
ap.add_argument('-i', help="input file", action="store")
ap.add_argument('-n', help="GTF id of the field to use as name in bed", action="store")

opts = ap.parse_args()

if opts.i is None or opts.n is None:
    print(usage)
    ap.print_help()
    sys.exit(1)

gtf = open(opts.i)
for i, line in enumerate(gtf):
    line = line.rstrip()  # remove trailing newline
    elements = line.split("\t")
    chr = elements[0]
    start = elements[3]
    end = elements[4]
    strand = elements[6]
    score = elements[9]
    name = "placeholdername"

    if score == ".":
        score = "NA"

    meta_elements = elements[8].strip().split(";")
    meta_dict = dict()
    for e in meta_elements:
	e = e.strip()
	if e == "":  # trailing ; in elements[8] creates a final empty item in the split array
	    continue

	parts = e.split(" ")
	key = parts[0]
	value = parts[1].replace("\"", "")
	meta_dict[key] = value

    name = meta_dict[opts.n]
    sys.stdout.write(chr + "\t" + start + "\t" + end + "\t" + name + "\t" + score + "\t" + strand + "\n")

gtf.close()
