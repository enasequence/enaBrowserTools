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
    parser.add_argument('-f', '--format', default='embl', choices=['embl', 'fasta', 'master'],
                        help='File format required (default is embl); master format only available for WGS')
    parser.add_argument('-d', '--dest', default='.',
                        help='Destination directory (default is current running directory)')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.1')
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
    return success

def download_wgs(dest_dir, accession, format):
    if utils.is_unversioned_wgs_set(accession):
        return download_unversioned_wgs(dest_dir, accession, format)
    else:
        return download_versioned_wgs(dest_dir, accession, format)

def download_versioned_wgs(dest_dir, accession, format):
    prefix = accession[:6]
    if format is None:
        format = utils.EMBL_FORMAT
    public_set_url = utils.get_wgs_ftp_url(prefix, utils.PUBLIC, format)
    supp_set_url = utils.get_wgs_ftp_url(prefix, utils.SUPPRESSED, format)
    success = utils.get_ftp_file(public_set_url, dest_dir)
    if not success:
        success = utils.get_ftp_file(supp_set_url, dest_dir)
    if not success:
        print 'No WGS set file available for ' + accession + ', format ' + format
        print 'Please contact ENA (datasubs@ebi.ac.uk) if you feel this set should be available'

def download_unversioned_wgs(dest_dir, accession, format):
    prefix = accession[:4]
    if format is None:
        format = utils.EMBL_FORMAT
    public_set_url = utils.get_nonversioned_wgs_ftp_url(prefix, utils.PUBLIC, format)
    if public_set_url is not None:
        utils.get_ftp_file(public_set_url, dest_dir)
    else:
        supp_set_url = utils.get_nonversion_supp_wgs_ftp_url(prefix, format)
        if supp_set_url is not None:
            utils.get_ftp_file(supp_set_url, dest_dir)
        else:
            print 'No WGS set file available for ' + accession + ', format ' + format
            print 'Please contact ENA (datasubs@ebi.ac.uk) if you feel this set should be available'

def check_format(format):
    allowed_formats = [utils.EMBL_FORMAT, utils.FASTA_FORMAT, utils.MASTER_FORMAT]
    if format not in allowed_formats:
        print 'Please select a valid format for this accession: ', allowed_formats
        sys.exit(1)

if __name__ == '__main__':
    parser = set_parser()
    args = parser.parse_args()

    accession = args.accession.upper()
    format = args.format
    dest_dir = args.dest

    try:
        if utils.is_wgs_set(accession):
            download_wgs(dest_dir, accession, format)
        elif utils.is_sequence(accession) or utils.is_coding(accession):
            if not utils.is_available(accession):
                print 'Record does not exist or is not available for accession provided'
                sys.exit(1)
            if format == utils.MASTER_FORMAT:
                print 'Invalid format. master format only available for WGS sets'
                sys.exit(1)
            download_sequence(dest_dir, accession, format)
        else:
            print 'Error: Invalid accession. A sequence or coding accession or a WGS set (prefix or master accession) must be provided'
            sys.exit(1)
        print 'Completed'
    except Exception:
        utils.print_error()
        sys.exit(1)
