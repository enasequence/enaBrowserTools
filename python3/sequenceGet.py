#
# sequenceGet.py
#

import sys
import argparse

import utils


def append_record(dest_file, accession, fmt):
    url = utils.get_record_url(accession, fmt)
    return utils.append_record(url, dest_file)

def download_sequence(dest_dir, accession, fmt, aspera):

    fmt = fmt or utils.EMBL_FORMAT

    success = utils.download_record(dest_dir, accession, fmt, aspera)
    if not success:
        msg = 'Unable to fetch file for {}, format {}'.format(accession, fmt)
        print(msg, file=sys.stderr)

def download_wgs(dest_dir, accession, fmt):

    fmt = fmt or utils.EMBL_FORMAT

    if utils.is_unversioned_wgs_set(accession):
        return download_unversioned_wgs(dest_dir, accession, fmt)
    else:
        return download_versioned_wgs(dest_dir, accession, fmt)

def download_versioned_wgs(dest_dir, accession, fmt):
    prefix = accession[:6]

    public_set_url = utils.get_wgs_ftp_url(prefix, utils.PUBLIC, fmt)
    supp_set_url = utils.get_wgs_ftp_url(prefix, utils.SUPPRESSED, fmt)
    success = utils.get_ftp_file(public_set_url, dest_dir)

    if not success:
        success = utils.get_ftp_file(supp_set_url, dest_dir)

    if not success:
        msg = 'No WGS set file available for {}, format {}\n\
               Please contact ENA (datasubs@ebi.ac.uk) if you \
               feel this set should be available'

        print(msg.format(accession, fmt), file=sys.stderr)

def download_unversioned_wgs(dest_dir, accession, fmt):
    prefix = accession[:4]

    public_set_url = utils.get_nonversioned_wgs_ftp_url(prefix, utils.PUBLIC, fmt)
    if public_set_url is not None:
        utils.get_ftp_file(public_set_url, dest_dir)
    else:
        supp_set_url = utils.get_nonversioned_supp_wgs_ftp_url(prefix, fmt)
        if supp_set_url is not None:
            utils.get_ftp_file(supp_set_url, dest_dir)
        else:

            msg = 'No WGS set file available for {}, format {}\n\
                   Please contact ENA (datasubs@ebi.ac.uk) if you \
                   feel this set should be available'

            print(msg.format(accession, fmt), file=sys.stderr)

def check_format(fmt):

    allowed_formats = [utils.EMBL_FORMAT, utils.FASTA_FORMAT, utils.MASTER_FORMAT]

    if fmt not in allowed_formats:

        msg = 'Please select a valid format for this accession: {}'
        print(msg.format(allowed_formats), file=sys.stderr)

        sys.exit(1)
