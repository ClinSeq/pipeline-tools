import logging
from collections import namedtuple

import click
import pysam
import sys
import vcf
from vcf.model import _Call as Call


@click.command()
@click.option('--loglevel', default='INFO', help='level of logging')
@click.option('--samplename', default=None, help="namf of the sample to add")
@click.argument('variant_file')
@click.argument('bam_file')
def main(variant_file, bam_file, samplename, loglevel):
    setup_logging(loglevel)
    vcf_reader = vcf.Reader(open(variant_file, 'r'))
    bamfile = pysam.AlignmentFile(bam_file, "rb")
    vcf_reader.samples.append(samplename)
    vcf_writer = vcf.Writer(open('/dev/stdout', 'w'), vcf_reader)
    for variant in vcf_reader:
        # only work on simple substitutions
        if len(variant.REF) == 1 and len(variant.ALT) == 1 and len(variant.ALT[0]) == 1:

            pile = bamfile.pileup(variant.CHROM, variant.POS, variant.POS + 1)
            bases = []
            quals = []
            for pileupcolumn in pile:
                if pileupcolumn.pos + 1 != variant.POS:
                    continue
                for pileupread in pileupcolumn.pileups:
                    if not pileupread.is_del and not pileupread.is_refskip:
                        bases.append(pileupread.alignment.query_sequence[pileupread.query_position])
                        quals.append(pileupread.alignment.query_qualities[pileupread.query_position])
            bases.sort()
            logging.debug("pileup at {}:{} {}/{} = {}".format(variant.CHROM, variant.POS, variant.REF, variant.ALT,
                                                              "".join(bases)))
            Genotype = namedtuple('Genotype', variant.FORMAT.split(":"))  # lazy genotype object
            Genotype.__new__.__defaults__ = ('.',) * len(Genotype._fields)  # set defaults to 0
            dp = len(bases)
            ro = len([base for base in bases if base == variant.REF])
            ao = len([base for base in bases if base == variant.ALT[0]])
            gt = "./."
            newgt = Genotype(AO=ao, RO=ro, DP=dp, GT=gt)
            newcall = Call(site=variant, sample=samplename, data=newgt)
            variant.samples.append(newcall)
            vcf_writer.write_record(variant)

    bamfile.close()
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
    logging.info("Started log with loglevel %(loglevel)s" % {"loglevel": loglevel})


if __name__ == "__main__":
    sys.exit(main())
