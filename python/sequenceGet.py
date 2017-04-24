#
# sequenceGet.py
#

import sys
import argparse

import utils

def set_parser():
    parser = argparse.ArgumentParser(prog='sequenceGet',
                                     description='Download sequence data for a given INSDC accession')
    parser.add_argument('accession', help='INSDC sequence/coding accession or WGS prefix (LLLLVV) to fetch')
    parser.add_argument('-f', '--format', default='embl', choices=['embl', 'fasta'],
                        help='File format required (default is embl)')
    parser.add_argument('-d', '--dest', default='.',
                        help='Destination directory (default is current running directory)')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    return parser

def append_record(dest_file, accession, format):
    url = utils.get_record_url(accession, format)
    return utils.append_record(url, dest_file)

def download_sequence(dest_dir, accession, format):
    if format is None:
        format = utils.EMBL_FORMAT
    success = utils.download_record(dest_dir, accession, format)
    if not success:
        print 'Unable to fetch file for ' + accession + ', format ' + format

def download_wgs(dest_dir, accession, format):
    if format is None:
        format = utils.EMBL_FORMAT
    public_set_url = utils.get_wgs_ftp_url(accession, utils.PUBLIC, format)
    supp_set_url = utils.get_wgs_ftp_url(accession, utils.SUPPRESSED, format)
    success = utils.get_ftp_file(public_set_url, dest_dir)
    if not success:
        success = utils.get_ftp_file(supp_set_url, dest_dir)
    if not success:
        print 'No WGS set file available for ' + accession + ', format ' + format
        print 'Please contact ENA (datasubs@ebi.ac.uk) if you feel this set should be available'

def check_format(format):
    if format not in [utils.EMBL_FORMAT, utils.FASTA_FORMAT]:
        print 'Please select a valid format for this accession: ', [utils.EMBL_FORMAT, utils.FASTA_FORMAT]
        sys.exit(1)

if __name__ == '__main__':
    parser = set_parser()
    args = parser.parse_args()

    accession = args.accession
    format = args.format
    dest_dir = args.dest

    try:
        if utils.is_sequence(accession) or utils.is_coding(accession):
            if not utils.is_available(accession):
                print 'Record does not exist or is not available for accession provided'
                sys.exit(1)
            download_sequence(dest_dir, accession, format)
        elif utils.is_wgs_set(accession):
            download_wgs(dest_dir, accession, format)
        else:
            print 'Error: Invalid accession. A sequence or coding accession or a WGS set prefix (LLLLVV) must be provided'
            sys.exit(1)
        print 'Download completed'
    except Exception:
        utils.print_error()
        sys.exit(1)
