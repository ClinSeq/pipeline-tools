#!/usr/bin/env python

"""Create report directories and yaml files in a defined project dir"""
import os
import argparse
import sys
import logging
import pyautoseq.report
import pyautoseq.readpair
import json

__author__ = 'dankle'


def main():
    opts = parse_cli()
    setup_logging(opts.loglevel)
    logging.debug("Opening files")

    reports = pyautoseq.report.Report.fromFile(opts.reports)
    readpairs = pyautoseq.readpair.Readpair.fromFile(opts.readpairs)

    for report in reports:
        logging.debug("Processing report {}".format(report.REPORTID))
        sample_conf_dir = "{outdir}/{reportid}".format(outdir=opts.outdir, reportid=report.REPORTID)
        logging.debug("Report dir is {}".format(sample_conf_dir))
        mkdir(sample_conf_dir)
        sample_conf_json = "{sample_conf_dir}/{reportid}.json".format(sample_conf_dir=sample_conf_dir, reportid=report.REPORTID)
        json_file = open(sample_conf_json, "w")
        json_file.write(json.dumps(report.do_dict(readpairs), indent=4, sort_keys=True))
        json_file.close()

    logging.debug("Done")


def mkdir(dir):
    """ Create a directory if it doesn't exist
    :param dir: dir to create
    """
    logging.debug("Creating dir {}".format(dir))
    if not os.path.isdir(dir):
        try:
            os.makedirs(dir)
        except OSError:
            logging.error("Couldn't create directory {}".format(dir))
    else:
        logging.debug("Skipped creating {} as it already exists.".format(dir))


def parse_cli():
    """
    Parse command line argument
    :return: a Namespace object from argparse.parse_args()
    """
    ap = argparse.ArgumentParser()
    ap.add_argument('-readpairs', help="readpairs (targets) file", action="store", required=True)
    ap.add_argument('-reports', help="report files", action="store", required=True)
    ap.add_argument('-outdir', help="output directory", action="store", required=True)
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

