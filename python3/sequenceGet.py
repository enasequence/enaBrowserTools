#
# sequenceGet.py
#
#
# Copyright 2017 EMBL-EBI, Hinxton outstation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys
import argparse

import utils


def write_record(dest_file, accession, output_format, expanded=False):
    url = utils.get_record_url(accession, output_format)
    if expanded:
        url = url + '&expanded=true'
    return utils.write_record(url, dest_file)

def download_sequence(dest_dir, accession, output_format, expanded):
    if output_format is None:
        output_format = utils.EMBL_FORMAT
    success = utils.download_record(dest_dir, accession, output_format, expanded)
    if not success:
        print ('Unable to fetch file for {0}, format {1}'.format(accession, output_format))

def download_wgs(dest_dir, accession, output_format):
    if utils.is_unversioned_wgs_set(accession):
        return download_unversioned_wgs(dest_dir, accession, output_format)
    else:
        return download_versioned_wgs(dest_dir, accession, output_format)

def download_versioned_wgs(dest_dir, accession, output_format):
    prefix = accession[:6]
    if output_format is None:
        output_format = utils.EMBL_FORMAT
    public_set_url = utils.get_wgs_ftp_url(prefix, utils.PUBLIC, output_format)
    supp_set_url = utils.get_wgs_ftp_url(prefix, utils.SUPPRESSED, output_format)
    success = utils.get_ftp_file(public_set_url, dest_dir)
    if not success:
        success = utils.get_ftp_file(supp_set_url, dest_dir)
    if not success:
        print ('No WGS set file available for {0}, format {1}'.format(accession, output_format))
        print ('Please contact ENA (datasubs@ebi.ac.uk) if you feel this set should be available')

def download_unversioned_wgs(dest_dir, accession, output_format):
    prefix = accession[:4]
    if output_format is None:
        output_format = utils.EMBL_FORMAT
    public_set_url = utils.get_nonversioned_wgs_ftp_url(prefix, utils.PUBLIC, output_format)
    if public_set_url is not None:
        utils.get_ftp_file(public_set_url, dest_dir)
    else:
        supp_set_url = utils.get_nonversioned_wgs_ftp_url(prefix, utils.SUPPRESSED, output_format)
        if supp_set_url is not None:
            utils.get_ftp_file(supp_set_url, dest_dir)
        else:
            print ('No WGS set file available for {0}, format {1}'.format(accession, output_format))
            print ('Please contact ENA (datasubs@ebi.ac.uk) if you feel this set should be available')

def check_format(output_format):
    allowed_formats = [utils.EMBL_FORMAT, utils.FASTA_FORMAT, utils.MASTER_FORMAT]
    if output_format not in allowed_formats:
        sys.stderr.write('Please select a valid format for this accession: {0}\n'.format(allowed_formats))
        sys.exit(1)
