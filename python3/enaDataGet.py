#
# enaDataGet.py
#

import argparse
import os
import sys

import sequenceGet
import assemblyGet
import readGet
import utils

def set_parser():
    parser = argparse.ArgumentParser(prog='enaDataGet',
                                     description = 'Download data for a given accession')
    parser.add_argument('accession', help="""Sequence, coding, assembly, run, experiment or
                                        analysis accession or WGS prefix (LLLLVV) to download """)
    parser.add_argument('-f', '--format', default=None,
                        choices=['embl', 'fasta', 'submitted', 'fastq', 'sra'],
                        help="""File format required. Format requested must be permitted for
                              data type selected. sequence, assembly and wgs accessions: embl(default) and fasta formats.
                              read group: submitted (default), fastq and sra formats. analysis group: submitted only.
                              Default is submitted""")
    parser.add_argument('-d', '--dest', default='.',
                        help='Destination directory (default is current running directory)')
    parser.add_argument('-w', '--wgs', action='store_true',
                        help='Download WGS set for each assembly if available (default is false)')
    parser.add_argument('-m', '--meta', action='store_true',
                        help='Download read or analysis XML in addition to data files (default is false)')
    parser.add_argument('-i', '--index', action='store_true',
                        help="""Download CRAM index files with submitted CRAM files, if any (default is false).
                            This flag is ignored for fastq and sra format options. """)
    parser.add_argument('-a', '--aspera', default=None,
                        help='Use the aspera command line client to download, instead of FTP, with the provided settings file.')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.3.1')
    return parser


if __name__ == '__main__':
    parser = set_parser()
    args = parser.parse_args()

    accession = args.accession
    format = args.format
    dest_dir = args.dest
    fetch_wgs = args.wgs
    fetch_meta = args.meta
    fetch_index = args.index
    aspera_settings = args.aspera

    aspera = False
    if aspera_settings is not None:
        aspera = True
        utils.set_aspera_variables(aspera_settings)

    try:
        if utils.is_wgs_set(accession):
            if format is not None:
                sequenceGet.check_format(format)
            sequenceGet.download_wgs(dest_dir, accession, format)
        elif not utils.is_available(accession):
            sys.stderr.write('ERROR: Record does not exist or is not available for accession provided\n')
            sys.exit(1)
        elif utils.is_sequence(accession):
            if format is not None:
                sequenceGet.check_format(format)
            sequenceGet.download_sequence(dest_dir, accession, format)
        elif utils.is_analysis(accession):
            if format is not None:
                readGet.check_read_format(format)
            readGet.download_files(accession, format, dest_dir, fetch_index, fetch_meta, aspera)
        elif utils.is_run(accession) or utils.is_experiment(accession):
            if format is not None:
                readGet.check_read_format(format)
            readGet.download_files(accession, format, dest_dir, fetch_index, fetch_meta, aspera)
        elif utils.is_assembly(accession):
            if format is not None:
                assemblyGet.check_format(format)
            assemblyGet.download_assembly(dest_dir, accession, format, fetch_wgs)
        else:
            sys.stderr.write('ERROR: Invalid accession provided\n')
            sys.exit(1)
        print ('Completed')
    except Exception:
        utils.print_error()
        sys.exit(1)
