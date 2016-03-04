#!/usr/bin/env python
"""target_coverage_histogram.py

Compute a coverage histogram for regions in a given bed file

usage: target_coverage_histogram.py --targets targets.bed aligned.bam > hist.txt

output format
# coverage\tnumber_of_bases_at_coverage
"""

import logging
from collections import namedtuple
import click
import pysam
import sys
import vcf
from vcf.model import _Call as Call


@click.command()
@click.option('--loglevel', default='INFO', help='level of logging')
@click.option('--targets', default=None, help="name of the sample to add")
@click.option('--min_basequal', default=30, help="minimum base quality to count")
@click.argument('bam_file')
def main(targets, bam_file, loglevel, min_basequal):
    setup_logging(loglevel)
    bedfileh = open(targets, 'r')
    bamfile = pysam.AlignmentFile(bam_file, "rb")

    histogram = {}

    for l in bedfileh:
        if not l.strip().startswith("#") and not l.strip() == "":
            (chrom, start, end) = l.split()[0:3]
            start = int(start)
            end = int(end)
            logging.debug("piling up in region {}:{}-{}".format(chrom, start, end))
            pile = bamfile.pileup(chrom, start, end)
            for pileupcolumn in pile:
                bases = []
                if start <= pileupcolumn.reference_pos <= end:
                    logging.debug("{}:{} depth={}".format(pileupcolumn.reference_name,
                                                          pileupcolumn.reference_pos,
                                                          pileupcolumn.nsegments))
                    for pileupread in pileupcolumn.pileups:
                        if not pileupread.is_del and not pileupread.is_refskip:
                            qual = pileupread.alignment.query_qualities[pileupread.query_position]
                            if qual >= min_basequal:
                                bases.append(pileupread.alignment.query_sequence[pileupread.query_position])

                    bases = [b for b in bases if b in "ATCG"]
                    coverage = len(bases)
                    logging.debug("coverage = {}".format(coverage))

                    if coverage not in histogram:
                        histogram[coverage] = 0

                    histogram[coverage] += 1

    bamfile.close()
    total_bases = sum(histogram.values())
    logging.debug("{}".format(histogram))
    sys.stdout.write("# target_coverage_histogram, bam: {}\n".format(bam_file))
    sys.stdout.write("# coverage\tbases_at_coverage\ttotal_bases\tfraction_bases_at_coverage\n")
    for k in sorted(histogram.keys()):
        sys.stdout.write("{}\t{}\t{}\t{}\n".format(k, histogram[k], total_bases, float(histogram[k])/total_bases))
    return 0


def setup_logging(loglevel="INFO"):
    """
    Set up logging
    :param loglevel: loglevel to use, one of ERROR, WARNING, DEBUG, INFO (default INFO)
    :return:
    """
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level,
                        format='%(levelname)s %(asctime)s %(funcName)s - %(message)s')
    logging.debug("Started log with loglevel %(loglevel)s" % {"loglevel": loglevel})


if __name__ == "__main__":
    sys.exit(main())
