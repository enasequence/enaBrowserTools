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
import xml.etree.ElementTree as ElementTree

import utils
import sequenceGet

REPLICON = 'assembled-molecule'
UNLOCALISED = 'unlocalised-scaffold'
UNPLACED = 'unplaced-scaffold'
PATCH = 'patch'

def check_format(output_format):
    if format not in [utils.EMBL_FORMAT, utils.FASTA_FORMAT]:
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

def download_sequence_set(accession_list, mol_type, assembly_dir, output_format, quiet):
    failed_accessions = []
    if len(accession_list) > 0:
        if not quiet:
            print 'fetching sequences: ' + mol_type
        target_file = os.path.join(assembly_dir, utils.get_filename(mol_type, output_format))
        for accession in accession_list:
            success = sequenceGet.append_record(target_file, accession, output_format)
            if not success:
                failed_accessions.append(accession)
    elif not quiet:
        print 'no sequences: ' + mol_type
    if len(failed_accessions) > 0:
        print 'Failed to fetch following ' + mol_type + ', format ' + output_format
        print failed_accessions.join(',')

def download_sequences(sequence_report, assembly_dir, output_format, quiet):
    local_sequence_report = os.path.join(assembly_dir, sequence_report)
    replicon_list, unlocalised_list, unplaced_list, patch_list = parse_sequence_report(local_sequence_report)
    download_sequence_set(replicon_list, REPLICON, assembly_dir, output_format, quiet)
    download_sequence_set(unlocalised_list, UNLOCALISED, assembly_dir, output_format, quiet)
    download_sequence_set(unplaced_list, UNPLACED, assembly_dir, output_format, quiet)
    download_sequence_set(patch_list, PATCH, assembly_dir, output_format, quiet)

def download_assembly(dest_dir, accession, output_format, fetch_wgs, quiet=False):
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
    # download wgs set if needed
    if wgs_set is not None and fetch_wgs:
        if not quiet:
            print 'fetching wgs set'
        sequenceGet.download_wgs(assembly_dir, wgs_set, output_format)
    # parse sequence report and download sequences
    if has_sequence_report:
        download_sequences(sequence_report.split('/')[-1], assembly_dir, output_format, quiet)
