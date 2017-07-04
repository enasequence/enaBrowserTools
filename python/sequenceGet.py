#
# sequenceGet.py
#

import sys
import argparse

import utils

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
        supp_set_url = utils.get_nonversioned_wgs_ftp_url(prefix, utils.SUPPRESSED, format)
        if supp_set_url is not None:
            utils.get_ftp_file(supp_set_url, dest_dir)
        else:
            print 'No WGS set file available for ' + accession + ', format ' + format
            print 'Please contact ENA (datasubs@ebi.ac.uk) if you feel this set should be available'

def check_format(format):
    allowed_formats = [utils.EMBL_FORMAT, utils.FASTA_FORMAT, utils.MASTER_FORMAT]
    if format not in allowed_formats:
        sys.stderr.write('Please select a valid format for this accession: {0}\n'.format(allowed_formats))
        sys.exit(1)
