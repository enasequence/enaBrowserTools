#
# enaGroupGet.py
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

import argparse
import os
import sys

import sequenceGet
import assemblyGet
import readGet
import utils
import traceback

def set_parser():
    parser = argparse.ArgumentParser(prog='enaGroupGet',
                                     description = 'Download data for a given study or sample, or (for sequence and assembly) taxon')
    parser.add_argument('accession', help='Study or sample accession or NCBI tax ID to fetch data for')
    parser.add_argument('-g', '--group', default='read',
                        choices=['sequence', 'wgs', 'assembly', 'read', 'analysis'],
                        help='Data group to be downloaded for this study/sample/taxon (default is read)')
    parser.add_argument('-f', '--format', default=None,
                        choices=['embl', 'fasta', 'submitted', 'fastq', 'sra'],
                        help="""File format required. Format requested must be permitted for
                              data group selected. sequence, assembly and wgs groups: embl and fasta formats.
                              read group: submitted, fastq and sra formats. analysis group: submitted only.""")
    parser.add_argument('-d', '--dest', default='.',
                        help='Destination directory (default is current running directory)')
    parser.add_argument('-w', '--wgs', action='store_true',
                        help='Download WGS set for each assembly if available (default is false)')
    parser.add_argument('-e', '--extract-wgs', action='store_true',
                        help='Extract WGS scaffolds for each assembly if available (default is false)')
    parser.add_argument('-exp', '--expanded', action='store_true',
                        help='Expand CON scaffolds when downloading embl format (default is false)')
    parser.add_argument('-m', '--meta', action='store_true',
                        help='Download read or analysis XML in addition to data files (default is false)')
    parser.add_argument('-i', '--index', action='store_true',
                        help="""Download CRAM index files with submitted CRAM files, if any (default is false).
                            This flag is ignored for fastq and sra format options. """)
    parser.add_argument('-a', '--aspera', action='store_true',
                        help='Use the aspera command line client to download, instead of FTP.')
    parser.add_argument('-as', '--aspera-settings', default=None,
                    help="""Use the provided settings file, will otherwise check
                        for environment variable or default settings file location.""")
    parser.add_argument('-t', '--subtree', action='store_true',
                        help='Include subordinate taxa (taxon subtree) when querying with NCBI tax ID (default is false)')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.5.3')
    return parser

def download_report(group, result, accession, temp_file, subtree):
    search_url = utils.get_group_search_query(group, result, accession, subtree)
    response = utils.get_report_from_portal(search_url)
    f = open(temp_file, 'wb')
    for line in response:
        f.write(line)
    f.flush()
    f.close()

def download_data(group, data_accession, output_format, group_dir, fetch_wgs, extract_wgs, expanded, fetch_meta, fetch_index, aspera):
    if group == utils.WGS:
        print ('Fetching ' + data_accession[:6])
        sequenceGet.download_wgs(group_dir, data_accession[:6], output_format)
    else:
        print ('Fetching ' + data_accession)
        if group == utils.ASSEMBLY:
            assemblyGet.download_assembly(group_dir, data_accession, output_format, fetch_wgs, extract_wgs, expanded, True)
        elif group in [utils.READ, utils.ANALYSIS]:
            readGet.download_files(data_accession, output_format, group_dir, fetch_index, fetch_meta, aspera)

def download_data_group(group, accession, output_format, group_dir, fetch_wgs, extract_wgs, fetch_meta, fetch_index, aspera, subtree, expanded):
    temp_file_path = os.path.join(group_dir, accession + '_temp.txt')
    download_report(group, utils.get_group_result(group), accession, temp_file_path, subtree)
    header = True
    with open(temp_file_path) as f:
        for line in f:
            if header:
                header = False
                continue
            data_accession = line.strip()
            download_data(group, data_accession, output_format, group_dir, fetch_wgs, extract_wgs, expanded, fetch_meta, fetch_index, aspera)
    os.remove(temp_file_path)

def download_sequence_result(dest_file, group_dir, result, accession, subtree, update_accs, expanded):
    temp_file_path = os.path.join(group_dir, 'temp.txt')
    download_report(utils.SEQUENCE, result, accession, temp_file_path, subtree)
    header = True
    with open(temp_file_path) as f:
        for line in f:
            if header:
                header = False
                continue
            data_accession = line.strip()
            write_record = False
            if result == utils.SEQUENCE_UPDATE_RESULT:
                update_accs.append(data_accession)
                write_record = True
            elif result == utils.SEQUENCE_RELEASE_RESULT:
                if data_accession not in update_accs:
                    write_record = True
            if write_record:
                sequenceGet.write_record(dest_file, data_accession, output_format)
                dest_file.flush()
    os.remove(temp_file_path)
    return update_accs

def download_sequence_group(accession, output_format, group_dir, subtree, expanded):
    print ('Downloading sequences')
    update_accs = []
    dest_file_path = os.path.join(group_dir, utils.get_filename(accession + '_sequences', output_format))
    dest_file = open(dest_file_path, 'wb')
    #sequence update
    update_accs = download_sequence_result(dest_file, group_dir, utils.SEQUENCE_UPDATE_RESULT, accession, subtree, update_accs, expanded)
    #sequence release
    update_accs = download_sequence_result(dest_file, group_dir, utils.SEQUENCE_RELEASE_RESULT, accession, subtree, update_accs, expanded)
    dest_file.close()

def download_group(accession, group, output_format, dest_dir, fetch_wgs, extract_wgs, fetch_meta, fetch_index, aspera, subtree, expanded):
    group_dir = os.path.join(dest_dir, accession)
    utils.create_dir(group_dir)
    if group == utils.SEQUENCE:
        download_sequence_group(accession, output_format, group_dir, subtree, expanded)
    else:
        download_data_group(group, accession, output_format, group_dir, fetch_wgs, extract_wgs, fetch_meta, fetch_index, aspera, subtree, expanded)

if __name__ == '__main__':
    parser = set_parser()
    args = parser.parse_args()

    accession = args.accession
    group = args.group
    output_format = args.format
    dest_dir = args.dest
    fetch_wgs = args.wgs
    extract_wgs = args.extract_wgs
    expanded = args.expanded
    fetch_meta = args.meta
    fetch_index = args.index
    aspera = args.aspera
    aspera_settings = args.aspera_settings
    subtree = args.subtree

    if aspera or aspera_settings is not None:
        aspera = utils.set_aspera(aspera_settings)

    if not utils.is_available(accession):
        sys.stderr.write('ERROR: Study/sample does not exist or is not available for accession provided.\n')
        sys.stderr.write('If you believe that it should be, please contact datasubs@ebi.ac.uk for assistance.\n')
        sys.exit(1)

    if not utils.is_study(accession) and not utils.is_sample(accession) and not utils.is_taxid(accession):
        sys.stderr.write(
         'ERROR: Invalid accession. Only sample and study/project accessions or NCBI tax ID supported\n'
        )
        sys.exit(1)

    if output_format is None:
        if group in (utils.READ, utils.ANALYSIS):
            output_format = utils.SUBMITTED_FORMAT
        else:
            output_format = utils.EMBL_FORMAT
    elif not utils.group_format_allowed(group, output_format, aspera):
        sys.stderr.write('ERROR: Illegal group and format combination provided.  Allowed:\n')
        sys.stderr.write('sequence, assembly and wgs groups: embl and fasta formats\n')
        sys.stderr.write('read group: submitted, fastq and sra formats\n')
        sys.stderr.write('analysis group: submitted format only\n')
        sys.exit(1)

    try:
        # disable read and analysis retrieval for taxon until added in size calculation and user response
        if utils.is_taxid(accession) and group in ['read', 'analysis']:
            print('Sorry, tax ID retrieval not yet supported for read and analysis')
            sys.exit(1)
        download_group(accession, group, output_format, dest_dir, fetch_wgs, extract_wgs, fetch_meta, fetch_index, aspera, subtree, expanded)
        print ('Completed')
    except Exception:
        traceback.print_exc()
        utils.print_error()
        sys.exit(1)
