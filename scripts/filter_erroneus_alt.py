#!/usr/bin/env python
"""
removes variants with missing ALT alleles or where REF == ALT
use `filter_erroneus_alt.py -V /dev/stdin` for streaming with pipes.
"""
__author__ = 'dankle'

import argparse
import sys

ap = argparse.ArgumentParser()
ap.add_argument('-V', help="VCF file", action="store")

opts = ap.parse_args()
vcf = opts.V

if vcf is None:
    ap.print_help()
    sys.exit(1)

fp = open(vcf)
for i, line in enumerate(fp):
    if line.startswith("#"):
        sys.stdout.write(line)
    else:
        elements = line.split("\t")
        if len(elements) >= 9:
            REF = elements[3]
            ALT = elements[4]
            if REF == ALT:
                sys.stderr.write("Skipped variant with identical REF ant ALT alleles: " + line)
            elif ALT == ".":
                sys.stderr.write("Skipped variant with missing ALT: " + line)
            else:
                sys.stdout.write(line)

fp.close()

