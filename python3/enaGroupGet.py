#
# enaGroupGet.py
#

import argparse
import os
import sys

import sequenceGet
import assemblyGet
import readGet
import utils

def set_parser():
    parser = argparse.ArgumentParser(prog='enaGroupGet',
                                     description = 'Download data for a given study or sample')
    parser.add_argument('accession', help='Study or sample accession to fetch data for')
    parser.add_argument('-g', '--group', default='read',
                        choices=['sequence', 'wgs', 'assembly', 'read', 'analysis'],
                        help='Data group to be downloaded for this study/sample (default is read)')
    parser.add_argument('-f', '--format', default=None,
                        choices=['embl', 'fasta', 'submitted', 'fastq', 'sra'],
                        help="""File format required. Format requested must be permitted for
                              data group selected. sequence, assembly and wgs groups: embl and fasta formats.
                              read group: submitted, fastq and sra formats. analysis group: submitted only.""")
    parser.add_argument('-d', '--dest', default='.',
                        help='Destination directory (default is current running directory)')
    parser.add_argument('-w', '--wgs', action='store_true',
                        help='Download WGS set for each assembly if available (default is false)')
    parser.add_argument('-m', '--meta', action='store_true',
                        help='Download read or analysis XML in addition to data files (default is false)')
    parser.add_argument('-i', '--index', action='store_true',
                        help="""Download CRAM index files with submitted CRAM files, if any (default is false).
                            This flag is ignored for fastq and sra format options. """)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    return parser

def download_report(group, result, accession, temp_file):
    search_url = utils.get_group_search_query(group, result, accession)
    response = utils.get_report_from_portal(search_url)
    f = open(temp_file, 'wb')
    for line in response:
        f.write(line)
    f.flush()
    f.close()

def download_data(group, data_accession, format, group_dir, fetch_wgs, fetch_meta, fetch_index):
    if group == utils.WGS:
        print ('fetching ' + data_accession[:6])
        sequenceGet.download_wgs(group_dir, data_accession[:6], format)
    else:
        print ('fetching ' + data_accession)
        if group == utils.ASSEMBLY:
            assemblyGet.download_assembly(group_dir, data_accession, format, fetch_wgs, True)
        elif group in [utils.READ, utils.ANALYSIS]:
            readGet.download_files(data_accession, format, group_dir, fetch_index, fetch_meta)

def download_data_group(group, accession, format, group_dir, fetch_wgs, fetch_meta, fetch_index):
    temp_file = os.path.join(group_dir, accession + '_temp.txt')
    download_report(group, utils.get_group_result(group), accession, temp_file)
    f = open(temp_file)
    header = True
    for line in f:
        if header:
            header = False
            continue
        data_accession = line.strip()
        download_data(group, data_accession, format, group_dir, fetch_wgs, fetch_meta, fetch_index)
    f.close()
    os.remove(temp_file)

def download_sequence_group(accession, format, study_dir):
    print('Downloading sequences')
    update_accs = []
    dest_file = os.path.join(study_dir, utils.get_filename(accession + '_sequences', format))
    #sequence update
    temp_file = os.path.join(study_dir, 'temp.txt')
    download_report(utils.SEQUENCE, utils.SEQUENCE_UPDATE_RESULT, accession, temp_file)
    f = open(temp_file)
    header = True
    for line in f:
        if header:
            header = False
            continue
        data_accession = line.strip()
        update_accs.append(data_accession)
        sequenceGet.append_record(dest_file, data_accession, format)
    f.close()
    os.remove(temp_file)
    #sequence release
    temp_file = os.path.join(study_dir, 'temp.txt')
    download_report(utils.SEQUENCE, utils.SEQUENCE_RELEASE_RESULT, accession, temp_file)
    f = open(temp_file)
    header = True
    for line in f:
        if header:
            header = False
            continue
        data_accession = line.strip()
        if data_accession not in update_accs:
            sequenceGet.append_record(dest_file, data_accession, format)
    f.close()
    os.remove(temp_file)

def download_group(accession, group, format, dest_dir, fetch_wgs, fetch_meta, fetch_index):
    group_dir = os.path.join(dest_dir, accession)
    utils.create_dir(group_dir)
    if group == utils.SEQUENCE:
        download_sequence_group(accession, format, group_dir)
    else:
        download_data_group(group, accession, format, group_dir, fetch_wgs, fetch_meta, fetch_index)


if __name__ == '__main__':
    parser = set_parser()
    args = parser.parse_args()

    accession = args.accession
    group = args.group
    format = args.format
    dest_dir = args.dest
    fetch_wgs = args.wgs
    fetch_meta = args.meta
    fetch_index = args.index

    if not utils.is_available(accession):
        print ('Study/sample does not exist or is not available for accession provided')
        print ('If you believe that it should be, please contact datasubs@ebi.ac.uk for assistance')
        sys.exit(1)

    if not utils.is_study(accession) and not utils.is_sample(accession):
        print ('Error: Invalid accession. Only sample and study/project accessions supported')
        sys.exit(1)

    if format is None:
        if group in (utils.READ, utils.ANALYSIS):
            format = utils.SUBMITTED_FORMAT
        else:
            format = utils.EMBL_FORMAT
    elif not utils.group_format_allowed(group, format):
        print ('Illegal group and format combination provided.  Allowed:')
        print ('sequence, assembly and wgs groups: embl and fasta formats')
        print ('read group: submitted, fastq and sra formats')
        print ('analysis group: submitted format only')
        sys.exit(1)

    try:
        download_group(accession, group, format, dest_dir, fetch_wgs, fetch_meta, fetch_index)
        print ('Download completed')
    except Exception:
        utils.print_error()
        sys.exit(1)
