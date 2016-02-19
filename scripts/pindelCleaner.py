#!/usr/bin/env python

"""
For high-coverage data, pindel reports variants that are sequencing errors due to homopolymers being hard to
sequence and/or amplify in library prep. Therefore, these variants need to be filtered after running pindel.

This script will break if input variants are multi-allelic. Split them using vcf_parser --split first.

Clean pindel output base on two criteria:
1. Require that HOMLEN < abs(SVLEN)+ X if frac < 20%, with X hardcoded to 2
2. Remove END tags as they sometimes cause problems downstream
"""
from vcf_parser.utils import build_info_string

__author__ = 'dankle'

import argparse
import sys
from vcf_parser import VCFParser
import logging

logging.basicConfig(level=logging.INFO)

FIELDS_TO_SKIP = ["END"]

ap = argparse.ArgumentParser()
ap.add_argument('-V', help="VCF file", action="store")
ap.add_argument('-o', help="Output VCF file", action="store")
ap.add_argument("--DEBUG", help="print DEBUGGING info to stderr", action="store_true")
opts = ap.parse_args()

if opts.V is None or opts.o is None:
    ap.print_help()
    sys.exit(1)

vcf_reader = VCFParser(opts.V)
vcf_writer = open(opts.o, 'wb')

# remove fields we don't want
for key in FIELDS_TO_SKIP:
    if key in vcf_reader.metadata.info_dict:
        vcf_reader.metadata.info_dict.pop(key, None)

# write header
for line in vcf_reader.metadata.print_header():
    vcf_writer.write(line)
    vcf_writer.write("\n")

# write body
for variant in vcf_reader:
    print_variant = False

    for key in FIELDS_TO_SKIP:
        if key in variant["info_dict"]:
            variant["info_dict"].pop(key, None)

    info = variant['info_dict']
    if 'HOMLEN' in info and 'SVLEN' in info:
        if len(info['HOMLEN']) > 1 or len(info['SVLEN']) > 1:
            raise ImportError("Won't parse multiallelic variant. Split them to biallelic using vcf_parser first.")

    HOMLEN = int(info['HOMLEN'][0])
    absSVLEN = abs(int(info["SVLEN"][0]))

    #  if allelic fraction > 20% in any sample, keep the variant
    #  (independent of microhomology)
    for sample in variant['genotypes']:
        gt = variant['genotypes'][sample]
        allelic_fraction = gt.alt_depth/(float(gt.alt_depth+gt.ref_depth))
        if allelic_fraction >= 0.20:
            print_variant = True

    #  if the local microhomology is short, keep the variant
    #  (independent of alleleic fractions)
    if HOMLEN < absSVLEN + 2:
        print_variant = True

    if print_variant:
        logging.debug("KEEPING VARIANT: {0}".format(variant))
        variant["INFO"] = build_info_string(variant["info_dict"])
        vcf_writer.write("\t".join([variant[head] for head in vcf_reader.header]))
        vcf_writer.write("\n")
    else:
        logging.debug("DISCARDING VARIANT: {0}".format(variant))
