#
# assemblyGet.py
#

import os
import sys
import argparse
import xml.etree.ElementTree as ElementTree

import utils
import sequenceGet

REPLICON = 'assembled-molecule'
UNLOCALISED = 'unlocalised-scaffold'
UNPLACED = 'unplaced-scaffold'
PATCH = 'patch'

def set_parser():
    parser = argparse.ArgumentParser(prog='assemblyGet',
                                     description='Download sequence data for a given assembly accession')
    parser.add_argument('accession',
                        help='INSDC assembly accession to fetch (will use latest version if no version given)')
    parser.add_argument('-f', '--format', default='embl', choices=['embl', 'fasta'],
                        help='File format required (default is embl)')
    parser.add_argument('-d', '--dest', default='.',
                        help='Destination directory (default is current running directory)')
    parser.add_argument('-w', '--wgs', action='store_true',
                        help='Download WGS set if available (default is false)')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.1')
    return parser

def check_format(format):
    if format not in [utils.EMBL_FORMAT, utils.FASTA_FORMAT]:
        print ('Please select a valid format for this accession: ', [utils.EMBL_FORMAT, utils.FASTA_FORMAT])
        sys.exit(1)

def get_sequence_report_url(record):
    for link in record.iter('URL_LINK'):
        label = (link.find('LABEL').text)
        if label == 'Sequence Report':
            return link.find('URL').text
    return None

def get_wgs_set_prefix(record):
    for wgs in record.iter('WGS_SET'):
        prefix = wgs.find('PREFIX').text
        version = wgs.find('VERSION').text
        if len(version) == 1:
            version = str(0) + version
        return prefix + version
    return None

def parse_assembly_xml(xml_file):
    record = ElementTree.parse(xml_file).getroot()
    sequence_report = get_sequence_report_url(record)
    wgs_set = get_wgs_set_prefix(record)
    return (wgs_set, sequence_report)

def parse_sequence_report(local_sequence_report):
    f = open(local_sequence_report)
    lines = f.readlines()
    f.close()
    replicon_list = [l.split('\t')[0] for l in lines[1:] if l.split('\t')[3] == REPLICON]
    unlocalised_list = [l.split('\t')[0] for l in lines[1:] if l.split('\t')[3] == UNLOCALISED]
    unplaced_list = [l.split('\t')[0] for l in lines[1:] if l.split('\t')[3] == UNPLACED]
    patch_list = [l.split('\t')[0] for l in lines[1:] if PATCH in l.split('\t')[3]]
    return (replicon_list, unlocalised_list, unplaced_list, patch_list)

def download_sequence_set(accession_list, mol_type, assembly_dir, format, quiet):
    failed_accessions = []
    if len(accession_list) > 0:
        if not quiet:
            print ('fetching sequences: ' + mol_type)
        target_file = os.path.join(assembly_dir, utils.get_filename(mol_type, format))
        for accession in accession_list:
            success = sequenceGet.append_record(target_file, accession, format)
            if not success:
                failed_accessions.append(accession)
    elif not quiet:
        print ('no sequences: ' + mol_type)
    if len(failed_accessions) > 0:
        print ('Failed to fetch following ' + mol_type + ', format ' + format)
        print (failed_accessions.join(','))

def download_sequences(sequence_report, assembly_dir, format, quiet):
    local_sequence_report = os.path.join(assembly_dir, sequence_report)
    replicon_list, unlocalised_list, unplaced_list, patch_list = parse_sequence_report(local_sequence_report)
    download_sequence_set(replicon_list, REPLICON, assembly_dir, format, quiet)
    download_sequence_set(unlocalised_list, UNLOCALISED, assembly_dir, format, quiet)
    download_sequence_set(unplaced_list, UNPLACED, assembly_dir, format, quiet)
    download_sequence_set(patch_list, PATCH, assembly_dir, format, quiet)

def download_assembly(dest_dir, accession, format, fetch_wgs, quiet=False):
    if format is None:
        format = utils.EMBL_FORMAT
    assembly_dir = os.path.join(dest_dir, accession)
    utils.create_dir(assembly_dir)
    # download xml
    utils.download_record(assembly_dir, accession, utils.XML_FORMAT)
    local_xml = utils.get_destination_file(assembly_dir, accession, utils.XML_FORMAT)
    # get wgs and sequence report info
    wgs_set, sequence_report = parse_assembly_xml(local_xml)
    has_sequence_report = False
    # download sequence report
    if sequence_report is not None:
        has_sequence_report = utils.get_ftp_file(sequence_report, assembly_dir)
    # download wgs set if needed
    if wgs_set is not None and fetch_wgs:
        if not quiet:
            print ('fetching wgs set')
        sequenceGet.download_wgs(assembly_dir, wgs_set, format)
    # parse sequence report and download sequences
    if has_sequence_report:
        download_sequences(sequence_report.split('/')[-1], assembly_dir, format, quiet)


if __name__ == '__main__':
    parser = set_parser()
    args = parser.parse_args()

    accession = args.accession
    format = args.format
    dest_dir = args.dest
    fetch_wgs = args.wgs

    if not utils.is_assembly(accession):
        print ('Error: Invalid accession. An assembly accession (GCA_ prefix) must be provided')
        sys.exit(1)

    if not utils.is_available(accession):
        print ('Record does not exist or is not available for accession provided')
        sys.exit(1)

    try:
        download_assembly(dest_dir, accession, format, fetch_wgs)
        print ('Completed')
    except Exception:
        utils.print_error()
        sys.exit(1)
