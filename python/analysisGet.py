#
# analysisGet.py
#

import os
import argparse

import readGet
import utils

def set_parser():
    parser = argparse.ArgumentParser(prog='analysisGet',
                            description='Download data for a given analysis accession')
    parser.add_argument('accession', help='Analysis accession to fetch')
    parser.add_argument('-d', '--dest', default='.',
                        help='Destination directory (default is current running directory)')
    parser.add_argument('-m', '--meta', action='store_true',
                        help='Download analysis XML in addition to data files (default is false)')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.1')
    return parser


if __name__ == '__main__':
    parser = set_parser()
    args = parser.parse_args()

    accession = args.accession
    dest_dir = args.dest
    fetch_meta = args.meta

    if not utils.is_analysis(accession):
        print 'Error: Invalid accession. An analysis accession must be provided'
        sys.exit(1)

    if not utils.is_available(accession):
        print 'Record does not exist or is not available for accession provided'
        sys.exit(1)

    try:
        readGet.download_files(accession, utils.SUBMITTED_FORMAT, dest_dir, False, fetch_meta)
        print 'Completed'
    except Exception:
        utils.print_error()
        sys.exit(1)
