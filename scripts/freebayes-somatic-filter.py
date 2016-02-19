#!/usr/bin/env python

"""Find somatic variants from a tumor normal pair called with freebayes"""
import vcf_parser

__author__ = 'dankle'

from vcf_parser import VCFParser
import argparse
import sys
import logging

def main():
    opts = parse_cli()
    setup_logging(opts.loglevel)
    logging.debug("Opening files")
    if opts.V == "-":
        variants = VCFParser(fsock=sys.stdin, split_variants=True)
    else:
        variants = VCFParser(infile=opts.V, split_variants=True)
    logging.debug(variants)

    variants.metadata.add_info('SOMATIC', '0', 'Flag', 'Somatic mutation')
    variants.metadata.add_filter(filter_id="PASS", description="Variant passes somatic filter")
    variants.metadata.add_filter(filter_id="REJECT", description="Variant fails somatic filter")
    for line in variants.metadata.print_header():
        print(line)

    for variant in variants:
        logging.debug("Variant is {}".format(variant))
        tumor_gt = variant['genotypes'][opts.tumorid]
        normal_gt = variant['genotypes'][opts.normalid]
        try: 
            tumor_lod = max(tumor_gt.phred_likelihoods[i] - tumor_gt.phred_likelihoods[0] for i in range(1, len(tumor_gt.phred_likelihoods)))
            normal_lod = min(normal_gt.phred_likelihoods[0] - normal_gt.phred_likelihoods[i] for i in range(1, len(normal_gt.phred_likelihoods)))
        except ValueError:
            tumor_lod = -10
            normal_lod = -10
            logging.warning("No LODs found for variant {}".format(variant['variant_id']))
            logging.warning("Setting LODs to -10")

        logging.debug("T/N LODs are {}/{}".format(tumor_lod, normal_lod))
        logging.debug("T/N LODs thresholds are {}/{}".format(opts.tlod, opts.nlod))
        is_somatic = normal_lod >= opts.nlod and tumor_lod >= opts.tlod
        logging.debug("Variant passes filters: {}".format(is_somatic))

        #print [variant[head] for head in variants.header]
        if is_somatic:
            variant['info_dict']['SOMATIC'] = []
            variant['FILTER'] = 'PASS'
        else:
            variant['FILTER'] = 'REJECT'

        if is_somatic or opts.keep_filtered:
            variant['INFO'] = vcf_parser.utils.build_info_string(variant['info_dict'])
            print('\t'.join([variant[head] for head in variants.header]))



def parse_cli():
    """
    Parse command line argument
    :return: a Namespace object from argparse.parse_args()
    """
    ap = argparse.ArgumentParser()
    ap.add_argument('-V', help="input vcf file", action="store", required=True)
    ap.add_argument('-tumorid', help="tumor ID as in VCF", action="store", required=True)
    ap.add_argument('-normalid', help="normal ID as in VCF", action="store", required=True)
    ap.add_argument('-tlod', help="tumor LOD threshold", action="store", default=3.5, type=float)
    ap.add_argument('-nlod', help="normal LOD threshold", action="store", default=3.5, type=float)
    ap.add_argument('-keep_filtered', help="Keep filtered variants in the output file", action="store_true")
    ap.add_argument("--loglevel", help="level of logging", default='INFO', type=str,
                    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    return ap.parse_args()

def setup_logging(loglevel="INFO"):
    """
    Set up logging
    :return:
    """
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level,
                        format='%(levelname)s %(asctime)s %(funcName)s - %(message)s')
    logging.info("Started log with loglevel %(loglevel)s" % {"loglevel":loglevel})

if __name__ == "__main__":
    sys.exit(main())

