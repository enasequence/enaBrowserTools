#
# assemblyGet.py
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

import os
import sys
import argparse
import gzip
import xml.etree.ElementTree as ElementTree

import utils
import sequenceGet

REPLICON = 'assembled-molecule'
UNLOCALISED = 'unlocalised-scaffold'
UNPLACED = 'unplaced-scaffold'
PATCH = 'patch'


def check_format(output_format):
    if output_format not in [utils.EMBL_FORMAT, utils.FASTA_FORMAT]:
        sys.stderr.write(
            'ERROR: Invalid format. Please select a valid format for this accession: {0}\n'.format([utils.EMBL_FORMAT, utils.FASTA_FORMAT])
        )
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

def extract_wgs_sequences(accession_list):
    wgs_sequences = [a for a in accession_list if utils.is_wgs_sequence(a)]
    other_sequences = [a for a in accession_list if not utils.is_wgs_sequence(a)]
    return wgs_sequences, other_sequences

def download_sequence_set(accession_list, mol_type, assembly_dir, output_format, expanded, quiet):
    failed_accessions = []
    count = 0
    sequence_cnt = len(accession_list)
    divisor = utils.get_divisor(sequence_cnt)
    if sequence_cnt > 0:
        if not quiet:
            print ('fetching {0} sequences: {1}'.format(sequence_cnt, mol_type))
        target_file_path = os.path.join(assembly_dir, utils.get_filename(mol_type, output_format))
        target_file = open(target_file_path, 'wb')
        for accession in accession_list:
            success = sequenceGet.write_record(target_file, accession, output_format, expanded)
            if not success:
                failed_accessions.append(accession)
            else:
                count += 1
                if count % divisor == 0 and not quiet:
                    print ('downloaded {0} of {1} sequences'.format(count, sequence_cnt))
        if not quiet:
            print ('downloaded {0} of {1} sequences'.format(count, sequence_cnt))
        target_file.close()
    elif not quiet:
        print ('no sequences: ' + mol_type)
    if len(failed_accessions) > 0:
        print ('Failed to fetch following {0}, format {1}'.format(mol_type, output_format))
        print (','.join(failed_accessions))

def download_sequences(sequence_report, assembly_dir, output_format, expanded, quiet):
    local_sequence_report = os.path.join(assembly_dir, sequence_report)
    replicon_list, unlocalised_list, unplaced_list, patch_list = parse_sequence_report(local_sequence_report)
    wgs_scaffolds, other_unlocalised = extract_wgs_sequences(unlocalised_list)
    wgs_unplaced, other_unplaced = extract_wgs_sequences(unplaced_list)
    download_sequence_set(replicon_list, REPLICON, assembly_dir, output_format, expanded, quiet)
    download_sequence_set(other_unlocalised, UNLOCALISED, assembly_dir, output_format, expanded, quiet)
    download_sequence_set(other_unplaced, UNPLACED, assembly_dir, output_format, expanded, quiet)
    download_sequence_set(patch_list, PATCH, assembly_dir, output_format, expanded, quiet)
    wgs_scaffolds.extend(wgs_unplaced)
    return wgs_scaffolds

def extract_wgs_scaffolds(assembly_dir, wgs_scaffolds, wgs_set, output_format, quiet):
    if not quiet:
        print ('extracting {0} WGS scaffolds from WGS set file'.format(len(wgs_scaffolds)))
    accs = [a.split('.')[0] for a in wgs_scaffolds]
    wgs_file_path = os.path.join(assembly_dir, wgs_set + utils.get_wgs_file_ext(output_format))
    target_file_path = os.path.join(assembly_dir, utils.get_filename('wgs_scaffolds', output_format))
    write_line = False
    target_file = open(target_file_path, 'w')
    with gzip.open(wgs_file_path, 'rb') as f:
        for line in f:
            if utils.record_start_line(line, output_format):
                if utils.extract_acc_from_line(line, output_format) in accs:
                    write_line = True
                else:
                    write_line = False
                    target_file.flush()
            if write_line:
                target_file.write(line)
    target_file.flush()
    target_file.close()

def download_assembly(dest_dir, accession, output_format, fetch_wgs, extract_wgs, expanded, quiet=False):
    if output_format is None:
        output_format = utils.EMBL_FORMAT
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
    # parse sequence report and download sequences
    wgs_scaffolds = []
    wgs_scaffold_cnt = 0
    if has_sequence_report:
        wgs_scaffolds = download_sequences(sequence_report.split('/')[-1], assembly_dir, output_format, expanded, quiet)
        wgs_scaffold_cnt = len(wgs_scaffolds)
        if wgs_scaffold_cnt > 0:
            if not quiet:
                print ('Assembly contains {} WGS scaffolds, will fetch WGS set'.format(wgs_scaffold_cnt))
            fetch_wgs = True
    else:
        fetch_wgs = True
    # download wgs set if needed
    if wgs_set is not None and fetch_wgs:
        if not quiet:
            print ('fetching wgs set')
        sequenceGet.download_wgs(assembly_dir, wgs_set, output_format)
        # extract wgs scaffolds from WGS file
        if wgs_scaffold_cnt > 0 and extract_wgs:
            extract_wgs_scaffolds(assembly_dir, wgs_scaffolds, wgs_set, output_format, quiet)
