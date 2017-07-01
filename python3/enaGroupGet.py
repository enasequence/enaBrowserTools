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
    parser.add_argument('-m', '--meta', action='store_true',
                        help='Download read or analysis XML in addition to data files (default is false)')
    parser.add_argument('-i', '--index', action='store_true',
                        help="""Download CRAM index files with submitted CRAM files, if any (default is false).
                            This flag is ignored for fastq and sra format options. """)
    parser.add_argument('-a', '--aspera', action='store_true',
                        help='Use the aspera command line client to download, instead of FTP (default is false).')
    parser.add_argument('-t', '--subtree', action='store_true',
                        help='Include subordinate taxa (taxon subtree) when querying with NCBI tax ID (default is false)')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.3')
    return parser

def download_report(group, result, accession, temp_file, subtree):
    search_url = utils.get_group_search_query(group, result, accession, subtree)
    response = utils.get_report_from_portal(search_url)

    with open(temp_file, 'wb') as f:
        for line in response:
            f.write(line)

def download_data(group, data_accession, format, group_dir, fetch_wgs, fetch_meta, fetch_index, aspera):
    if group == utils.WGS:
        print ('Fetching ' + data_accession[:6])
        if aspera:
            print ('Aspera not supported for WGS data. Using FTP...')
        sequenceGet.download_wgs(group_dir, data_accession[:6], format)
    else:
        print ('Fetching ' + data_accession)
        if group == utils.ASSEMBLY:
            if aspera:
                print ('Aspera not supported for assembly data. Using FTP...')
            assemblyGet.download_assembly(group_dir, data_accession, format, fetch_wgs, True)
        elif group in [utils.READ, utils.ANALYSIS]:
            readGet.download_files(data_accession, format, group_dir, fetch_index, fetch_meta, aspera)

def download_data_group(group, accession, format, group_dir, fetch_wgs, fetch_meta, fetch_index, aspera, subtree):
    temp_file = os.path.join(group_dir, accession + '_temp.txt')
    download_report(group, utils.get_group_result(group), accession, temp_file, subtree)
    f = open(temp_file)
    header = True
    for line in f:
        if header:
            header = False
            continue
        data_accession = line.strip()
        download_data(group, data_accession, format, group_dir, fetch_wgs, fetch_meta, fetch_index, aspera)
    f.close()
    os.remove(temp_file)

def download_sequence_group(accession, format, group_dir, subtree):
    print('Downloading sequences')
    update_accs = []
    dest_file = os.path.join(group_dir, utils.get_filename(accession + '_sequences', format))
    #sequence update
    temp_file = os.path.join(group_dir, 'temp.txt')
    download_report(utils.SEQUENCE, utils.SEQUENCE_UPDATE_RESULT, accession, temp_file, subtree)
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
    temp_file = os.path.join(group_dir, 'temp.txt')
    download_report(utils.SEQUENCE, utils.SEQUENCE_RELEASE_RESULT, accession, temp_file, subtree)
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

def download_group(accession, group, format, dest_dir, fetch_wgs, fetch_meta, fetch_index, aspera, subtree):
    group_dir = os.path.join(dest_dir, accession)
    utils.create_dir(group_dir)
    if group == utils.SEQUENCE:
        if aspera:
            print ('Aspera not supported for sequence downloads. Using FTP...')
        download_sequence_group(accession, format, group_dir, subtree)
    else:
        download_data_group(group, accession, format, group_dir, fetch_wgs, fetch_meta, fetch_index, aspera, subtree)

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
    aspera = args.aspera
    subtree = args.subtree

    if not utils.is_available(accession):
        sys.stderr.write('ERROR: Study/sample does not exist or is not available for accession provided.\n')
        sys.stderr.write('If you believe that it should be, please contact datasubs@ebi.ac.uk for assistance.\n')
        sys.exit(1)

    if not utils.is_study(accession) and not utils.is_sample(accession) and not utils.is_taxid(accession):
        sys.stderr.write(
         'ERROR: Invalid accession. Only sample and study/project accessions or NCBI tax ID supported\n'
        )
        sys.exit(1)

    if format is None:
        if group in (utils.READ, utils.ANALYSIS):
            format = utils.SUBMITTED_FORMAT
        else:
            format = utils.EMBL_FORMAT
    elif not utils.group_format_allowed(group, format, aspera):
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
        download_group(accession, group, format, dest_dir, fetch_wgs, fetch_meta, fetch_index, aspera, subtree)
        print ('Completed')
    except Exception:
        utils.print_error()
        sys.exit(1)
