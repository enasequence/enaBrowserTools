#
# readGet.py
#

import os
import sys
import argparse

import utils

def set_parser():
    parser = argparse.ArgumentParser(prog='readGet',
                            description='Download sequence data for a given INSDC run/experiment accession')
    parser.add_argument('accession', help='INSDC run/experiment accession to fetch')
    parser.add_argument('-f', '--format', default='submitted', choices=['submitted', 'fastq', 'sra'],
                        help='File format required (default is submitted)')
    parser.add_argument('-d', '--dest', default='.',
                        help='Destination directory (default is current running directory)')
    parser.add_argument('-m', '--meta', action='store_true',
                        help='Download run and experiment XML in addition to data files (default is false)')
    parser.add_argument('-i', '--index', action='store_true',
                        help="""Download CRAM index files with submitted CRAM files, if any (default is false).
                            This flag is ignored for fastq and sra format options""")
    parser.add_argument('-a', '--aspera', action='store_true',
                        help='Use the aspera command line client to download, instead of FTP (default is false).')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    return parser

def check_read_format(format):
    if format not in [utils.SUBMITTED_FORMAT, utils.FASTQ_FORMAT, utils.SRA_FORMAT]:
        print 'Please select a valid format for this accession: ', \
            [utils.SUBMITTED_FORMAT, utils.FASTQ_FORMAT, utils.SRA_FORMAT]
        sys.exit(1)

def check_analysis_format(format):
    if format != utils.SUBMITTED_FORMAT:
        print 'Please select a valid format for this accession: ', utils.SUBMITTED_FORMAT
        sys.exit(1)

def download_file_with_md5_check(file_url, dest_dir, md5, aspera):
    print 'Downloading file with md5 check:' + file_url
    success=False
    if aspera:
        success = utils.get_aspera_file_with_md5_check(file_url, dest_dir, md5)
    else:
        success = utils.get_ftp_file_with_md5_check('ftp://' + file_url, dest_dir, md5)
        if not success:
            success = utils.get_ftp_file_with_md5_check('ftp://' + file_url, dest_dir, md5)
    if not success:
        print 'Failed to download file'

def download_file(file_url, dest_dir, aspera):
    print 'Downloading file:' + file_url
    success=False
    if aspera:
        success = utils.get_aspera_file(file_url, dest_dir)
    else:
        success = utils.get_ftp_file('ftp://' + file_url, dest_dir)
        if not success:
            success = utils.get_ftp_file('ftp://' + file_url, dest_dir)
    if not success:
        print 'Failed to download file'

def download_meta(accession, dest_dir):
    utils.download_record(dest_dir, accession, utils.XML_FORMAT)

def download_experiment_meta(run_accession, dest_dir):
    search_url = utils.get_experiment_search_query(run_accession)
    response = utils.get_report_from_portal(search_url)
    header = True
    for line in response:
        if header:
            header = False
            continue
        experiment_accession = line.strip().split('\t')[-1]
        break
    download_meta(experiment_accession, dest_dir)

def download_files(accession, format, dest_dir, fetch_index, fetch_meta, aspera):
    if format is None:
        format = utils.SUBMITTED_FORMAT
    accession_dir = os.path.join(dest_dir, accession)
    utils.create_dir(accession_dir)
    # download experiment xml
    is_experiment = utils.is_experiment(accession)
    if fetch_meta and is_experiment:
        download_meta(accession, accession_dir)
    # TODO download experiment xml for run accession
    if fetch_meta and utils.is_run(accession):
        download_experiment_meta(accession, accession_dir)
    # download data files
    search_url = utils.get_file_search_query(accession, format, fetch_index, aspera)
    temp_file = os.path.join(dest_dir, 'temp.txt')
    utils.download_report_from_portal(search_url, temp_file)
    f = open(temp_file)
    lines = f.readlines()
    f.close()
    os.remove(temp_file)
    for line in lines[1:]:
        data_accession, filelist, md5list, indexlist = utils.parse_file_search_result_line(line, accession,
                                                                                           format, fetch_index)
        # create run directory if downloading all data for an experiment
        if is_experiment:
            run_dir = os.path.join(accession_dir, data_accession)
            utils.create_dir(run_dir)
            target_dir = run_dir
        else:
            target_dir = accession_dir
        # download run/analysis XML
        if fetch_meta:
            download_meta(data_accession, target_dir)
        if len(filelist) == 0:
            print 'No files of format ' + format + ' for ' + data_accession
            continue
        for i in range(len(filelist)):
            file_url = filelist[i]
            md5 = md5list[i]
            if file_url != '':
                download_file_with_md5_check(file_url, target_dir, md5, aspera)
        for index_file in indexlist:
            if index_file != '':
                download_file(index_file, target_dir, aspera)


if __name__ == '__main__':
    parser = set_parser()
    args = parser.parse_args()

    accession = args.accession
    format = args.format
    dest_dir = args.dest
    fetch_meta = args.meta
    fetch_index = args.index
    aspera = args.aspera

    if not utils.is_run(accession) and not utils.is_experiment(accession):
        print 'Error: Invalid accession. An INSDC run or experiment accession must be provided'
        sys.exit(1)

    if not utils.is_available(accession):
        print 'Record does not exist or is not available for accession provided'
        sys.exit(1)

    try:
        download_files(accession, format, dest_dir, fetch_index, fetch_meta, aspera)
        print 'Download completed'
    except Exception:
        utils.print_error()
        sys.exit(1)
