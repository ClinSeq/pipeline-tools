#!/usr/bin/env python

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
            if REF != ALT :
                sys.stdout.write(line)
            else:
                sys.stderr.write("Skipped variant with identical REF ant ALT alleles: " + line)

fp.close()

