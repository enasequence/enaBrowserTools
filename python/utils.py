#
# utils.py
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

import base64
import ftplib
import hashlib
import re
import os
import sys
import urllib
import urllib2
import pexpect
import time
import shlex
import json
from datetime import datetime
import xml.etree.ElementTree as ElementTree
from subprocess import call, Popen, PIPE, STDOUT

from ConfigParser import SafeConfigParser

ASPERA_BIN = 'ascp' # ascp binary
ASPERA_PRIVATE_KEY = '/path/to/aspera_dsa.openssh' # ascp private key file
ASPERA_OPTIONS = '' # set any extra aspera options
ASPERA_SPEED = '100M' # set aspera download speed

ANON_USER = 'anon'
ANON_PWD = 'anon'

SUPPRESSED = 'suppressed'
PUBLIC = 'public'

XML_FORMAT = 'xml'
EMBL_FORMAT = 'embl'
FASTA_FORMAT = 'fasta'
MASTER_FORMAT = 'master'
SUBMITTED_FORMAT = 'submitted'
FASTQ_FORMAT = 'fastq'
SRA_FORMAT = 'sra'

XML_EXT = '.xml'
EMBL_EXT = '.dat'
FASTA_EXT = '.fasta'
WGS_EMBL_EXT = '.dat.gz'
WGS_FASTA_EXT = '.fasta.gz'
WGS_MASTER_EXT = '.master.dat'

SEQUENCE = 'sequence'
CODING = 'coding'
WGS = 'wgs'
RUN = 'run'
EXPERIMENT = 'experiment'
ANALYSIS = 'analysis'
ASSEMBLY = 'assembly'
STUDY = 'study'
READ = 'read'
SAMPLE = 'sample'
TAXON = 'taxon'

VIEW_URL_BASE = 'http://www.ebi.ac.uk/ena/data/view/'
XML_DISPLAY = '&display=xml'
EMBL_DISPLAY = '&display=text'
FASTA_DISPLAY = '&display=fasta'

READ_RESULT_ID='read_run'
ANALYSIS_RESULT_ID='analysis'
WGS_RESULT_ID='wgs_set'
ASSEMBLY_RESULT_ID='assembly'
SEQUENCE_UPDATE_ID='sequence_update'
SEQUENCE_RELEASE_ID='sequence_release'

WGS_FTP_BASE = 'ftp://ftp.ebi.ac.uk/pub/databases/ena/wgs'
WGS_FTP_DIR = 'pub/databases/ena/wgs'

PORTAL_SEARCH_BASE = 'http://www.ebi.ac.uk/ena/portal/api/search?'
RUN_RESULT = 'result=read_run'
ANALYSIS_RESULT = 'result=analysis'
WGS_RESULT = 'result=wgs_set'
ASSEMBLY_RESULT = 'result=assembly'
SEQUENCE_UPDATE_RESULT = 'result=sequence_update'
SEQUENCE_RELEASE_RESULT = 'result=sequence_release'

FASTQ_FIELD = 'fastq_ftp'
SUBMITTED_FIELD = 'submitted_ftp'
SRA_FIELD = 'sra_ftp'
INDEX_FIELD = 'cram_index_ftp'
FASTQ_MD5_FIELD = 'fastq_md5'
SUBMITTED_MD5_FIELD = 'submitted_md5'
SRA_MD5_FIELD = 'sra_md5'
INDEX_MD5_FIELD = None
FASTQ_ASPERA_FIELD = 'fastq_aspera'
SUBMITTED_ASPERA_FIELD = 'submitted_aspera'
SRA_ASPERA_FIELD = 'sra_aspera'
INDEX_ASPERA_FIELD = 'cram_index_aspera'

sequence_pattern_1 = re.compile('^[A-Z]{1}[0-9]{5}(\.[0-9]+)?$')
sequence_pattern_2 = re.compile('^[A-Z]{2}[0-9]{6}(\.[0-9]+)?$')
wgs_sequence_pattern = re.compile('^[A-Z]{4}[0-9]{8,9}(\.[0-9]+)?$')
coding_pattern = re.compile('^[A-Z]{3}[0-9]{5}(\.[0-9]+)?$')
wgs_prefix_pattern = re.compile('^[A-Z]{4}[0-9]{2}$')
wgs_master_pattern = re.compile('^[A-Z]{4}[0-9]{2}[0]{6}$')
unversion_wgs_prefix_pattern = re.compile('^[A-Z]{4}$')
unversion_wgs_master_pattern = re.compile('^[A-Z]{4}[0]{8}$')
run_pattern = re.compile('^[EDS]RR[0-9]{6,7}$')
experiment_pattern = re.compile('^[EDS]RX[0-9]{6,7}$')
analysis_pattern = re.compile('^[EDS]RZ[0-9]{6,7}$')
assembly_pattern = re.compile('^GCA_[0-9]{9}(\.[0-9]+)?$')
study_pattern_1 = re.compile('^[EDS]RP[0-9]{6,7}$')
study_pattern_2 = re.compile('^PRJ[EDN][AB][0-9]+$')
sample_pattern_1 = re.compile('^SAM[ND][0-9]{8}$')
sample_pattern_2 = re.compile('^SAMEA[0-9]{6,}$')
sample_pattern_3 = re.compile('^[EDS]RS[0-9]{6,7}$')

enaBrowserTools_path = os.path.dirname(os.path.dirname(__file__))

def is_available(accession):
    if is_taxid(accession):
        url = get_record_url('Taxon:{0}'.format(accession), XML_FORMAT)
    else:
        url = get_record_url(accession, XML_FORMAT)
    response = urllib2.urlopen(url)
    record = ElementTree.parse(response).getroot()
    return (not 'entry is not found' in record.text) and (len(record.getchildren()) > 0)

def is_sequence(accession):
    return sequence_pattern_1.match(accession) or sequence_pattern_2.match(accession)

def is_wgs_sequence(accession):
    return wgs_sequence_pattern.match(accession)

def is_coding(accession):
    return coding_pattern.match(accession)

def is_wgs_set(accession):
    return wgs_prefix_pattern.match(accession) \
        or wgs_master_pattern.match(accession) \
        or unversion_wgs_prefix_pattern.match(accession) \
        or unversion_wgs_master_pattern.match(accession)

def is_unversioned_wgs_set(accession):
    return unversion_wgs_prefix_pattern.match(accession) \
        or unversion_wgs_master_pattern.match(accession)

def is_run(accession):
    return run_pattern.match(accession)

def is_experiment(accession):
    return experiment_pattern.match(accession)

def is_analysis(accession):
    return analysis_pattern.match(accession)

def is_assembly(accession):
    return assembly_pattern.match(accession)

def is_study(accession):
    return study_pattern_1.match(accession) or study_pattern_2.match(accession)

def is_sample(accession):
    return sample_pattern_1.match(accession) or sample_pattern_2.match(accession) \
        or sample_pattern_3.match(accession)

def is_primary_study(accession):
    return study_pattern_2.match(accession)

def is_secondary_study(accession):
    return study_pattern_1.match(accession)

def is_primary_sample(accession):
    return sample_pattern_1.match(accession) or sample_pattern_2.match(accession)

def is_secondary_sample(accession):
    return sample_pattern_3.match(accession)

def is_taxid(accession):
    try:
        int(accession)
        return True
    except ValueError:
        return False

def get_accession_type(accession):
    if is_study(accession):
        return STUDY
    elif is_run(accession):
        return RUN
    elif is_experiment(accession):
        return EXPERIMENT
    elif is_analysis(accession):
        return ANALYSIS
    elif is_assembly(accession):
        return ASSEMBLY
    elif is_wgs_set(accession):
        return WGS
    elif is_coding(accession):
        return CODING
    elif is_sequence(accession):
        return SEQUENCE
    elif is_taxid(accession):
        return TAXON
    return None

def accession_format_allowed(accession, output_format, aspera):
    if is_analysis(accession):
        return output_format == SUBMITTED_FORMAT
    if is_run(accession) or is_experiment(accession):
        if aspera:
            return output_format in [SUBMITTED_FORMAT, FASTQ_FORMAT, SRA_ASPERA_FIELD]
        else:
            return output_format in [SUBMITTED_FORMAT, FASTQ_FORMAT, SRA_FIELD]
    return output_format in [EMBL_FORMAT, FASTA_FORMAT]

def group_format_allowed(group, output_format, aspera):
    if group == ANALYSIS:
        return output_format == SUBMITTED_FORMAT
    if group == READ:
        if aspera:
            return output_format in [SUBMITTED_FORMAT, FASTQ_FORMAT, SRA_ASPERA_FIELD]
        else:
            return output_format in [SUBMITTED_FORMAT, FASTQ_FORMAT, SRA_FIELD]
    return output_format in [EMBL_FORMAT, FASTA_FORMAT]

# assumption is that accession and format have already been vetted before this method is called
def get_record_url(accession, output_format):
    if output_format == XML_FORMAT:
        return VIEW_URL_BASE + accession + XML_DISPLAY
    elif output_format == EMBL_FORMAT:
        return VIEW_URL_BASE + accession + EMBL_DISPLAY
    elif output_format == FASTA_FORMAT:
        return VIEW_URL_BASE + accession + FASTA_DISPLAY
    return None

def get_filename(base_name, output_format):
    if output_format == XML_FORMAT:
        return base_name + XML_EXT
    elif output_format == EMBL_FORMAT:
        return base_name + EMBL_EXT
    elif output_format == FASTA_FORMAT:
        return base_name + FASTA_EXT
    return None

def get_destination_file(dest_dir, accession, output_format):
    filename = get_filename(accession, output_format)
    if filename is not None:
        return os.path.join(dest_dir, filename)
    return None

def download_single_record(url, dest_file):
    urllib.urlretrieve(url, dest_file)

def download_record(dest_dir, accession, output_format, expanded=False):
    try:
        dest_file = get_destination_file(dest_dir, accession, output_format)
        url = get_record_url(accession, output_format)
        if (expanded):
            url = url + '&expanded=true'
        download_single_record(url, dest_file)
        return True
    except Exception:
        return False

def write_record(url, dest_file):
    try:
        response = urllib2.urlopen(url)
        linenum = 1
        for line in response:
            if linenum == 1 and line.startswith('Entry:'):
                return False
            dest_file.write(line)
            linenum += 1
        dest_file.flush()
        return True
    except Exception:
        return False

def get_ftp_file(ftp_url, dest_dir, handler=None):
    try:
        filename = ftp_url.split('/')[-1]
        dest_file = os.path.join(dest_dir, filename)
        response = urllib.urlopen(ftp_url)
        chunk_read(response, file_handle=dest_file, handler=handler)
        return True
    except Exception:
        return False

def get_aspera_file(aspera_url, dest_dir, handler=None):
    try:
        filename = aspera_url.split('/')[-1]
        dest_file = os.path.join(dest_dir, filename)
        asperaretrieve(aspera_url, dest_dir, dest_file, handler=handler)
        return True
    except Exception:
        return False

def get_md5(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def check_md5(filepath, expected_md5, handler):
    generated_md5 = get_md5(filepath)
    if expected_md5 != generated_md5:
        if not handler:
            handler=sys.stdout.write
        handler('MD5 mismatch for downloaded file ' + filepath + '. Deleting file')
        handler('Generated md5: %s' % generated_md5)
        handler('Expected md5: %s' % expected_md5)
        os.remove(filepath)
        return False
    return True

def file_exists(file_url, dest_dir, md5):
    filename = file_url.split('/')[-1]
    local_file = os.path.join(dest_dir, filename)
    if os.path.isfile(local_file):
        generated_md5 = get_md5(local_file)
        if generated_md5 == md5:
            print '{0} already exists in local directory, skipping'.format(filename)
            return True
    return False

def get_ftp_file_with_md5_check(ftp_url, dest_dir, md5, handler=None):
    try:
        filename = ftp_url.split('/')[-1]
        dest_file = os.path.join(dest_dir, filename)
        response = urllib.urlopen(ftp_url)
        chunk_read(response, file_handle=dest_file, handler=handler)
        return check_md5(dest_file, md5, handler=handler)
    except Exception as e:
        sys.stderr.write("Error with FTP transfer: {0}\n".format(e))
        return False

def get_aspera_file_with_md5_check(aspera_url, dest_dir, md5, handler=None):
    try:
        filename = aspera_url.split('/')[-1]
        dest_file = os.path.join(dest_dir, filename)
        success = asperaretrieve(aspera_url, dest_dir, dest_file, handler=handler)
        if success:
            return check_md5(dest_file, md5, handler=handler)
        return success
    except Exception as e:
        sys.stderr.write("Error with Aspera transfer: {0}\n".format(e))
        return False

def set_aspera_variables(filepath):
    try:
        parser = SafeConfigParser()
        parser.read(filepath)
        # set and check binary location
        global ASPERA_BIN
        ASPERA_BIN = parser.get('aspera', 'ASPERA_BIN')
        if not os.path.exists(ASPERA_BIN):
            print 'Aspera binary ({0}) does not exist. Defaulting to FTP transfer'.format(ASPERA_BIN)
            return False
        if not os.access(ASPERA_BIN, os.X_OK):
            print 'You do not have permissions to execute the aspera binary ({0}). Defaulting to FTP transfer'.format(ASPERA_BIN)
            return False
        # set and check private key location
        global ASPERA_PRIVATE_KEY
        ASPERA_PRIVATE_KEY = parser.get('aspera', 'ASPERA_PRIVATE_KEY')
        if not os.path.exists(ASPERA_PRIVATE_KEY):
            print 'Private key file ({0}) does not exist. Defaulting to FTP transfer'.format(ASPERA_PRIVATE_KEY)
            return False
        # set non-file variables
        global ASPERA_SPEED
        ASPERA_SPEED = parser.get('aspera', 'ASPERA_SPEED')
        global ASPERA_OPTIONS
        ASPERA_OPTIONS = parser.get('aspera', 'ASPERA_OPTIONS')
        return True
    except Exception as e:
        sys.stderr.write("ERROR: cannot read aspera settings from {0}.\n".format(filepath))
        sys.stderr.write("{0}\n".format(e))
        sys.exit(1)

def set_aspera(aspera_filepath):
    aspera = True
    if aspera_filepath is not None:
        if os.path.exists(aspera_filepath):
            aspera = set_aspera_variables(aspera_filepath)
        else:
            print 'Cannot find {0} file, defaulting to FTP transfer'.format(aspera_filepath)
            aspera = False
    elif os.environ.get('ENA_ASPERA_INIFILE'):
        aspera = set_aspera_variables(os.environ.get('ENA_ASPERA_INIFILE'))
    else:
        if os.path.exists(os.path.join(enaBrowserTools_path, 'aspera_settings.ini')):
            aspera = set_aspera_variables(os.path.join(enaBrowserTools_path, 'aspera_settings.ini'))
        else:
            print 'Cannot find aspera_settings.ini file, defaulting to FTP transfer'
            aspera = False
    return aspera

def asperaretrieve(url, dest_dir, dest_file, handler=None):
    try:
        logdir=os.path.abspath(os.path.join(dest_dir, "logs"))
        create_dir(logdir)
        aspera_line="{bin} -QT -L {logs} -l {speed} -P33001 {aspera} -i {key} era-fasp@{file} {outdir}"
        aspera_line=aspera_line.format(
            bin=ASPERA_BIN,
            outdir=dest_dir,
            logs=logdir,
            file=url,
            aspera=ASPERA_OPTIONS,
            key=ASPERA_PRIVATE_KEY,
            speed=ASPERA_SPEED,
        )
        _do_aspera_pexpect(url, aspera_line, handler)
        return True
    except Exception as e:
        sys.stderr.write("Error with Aspera transfer: {0}\n".format(e))
        return False

def _do_aspera_pexpect(url, cmd, handler):
    thread = pexpect.spawn(cmd, timeout=None)
    cpl = thread.compile_pattern_list([pexpect.EOF, '(.+)'])
    started = 0

    while True:
        i = thread.expect_list(cpl, timeout=None)
        if i == 0:
            if started == 0:
                if handler and callable(handler):
                    handler("Error initiating transfer")
                else:
                    sys.stderr.write("Error initiating transfer")
            break
        elif i == 1:
            started = 1
            output = dict()
            pexp_match = thread.match.group(1)
            prev_file = ''
            tokens_to_match = ["Mb/s"]
            units_to_match = ["KB", "MB", "GB"]
            rates_to_match = ["Kb/s", "kb/s", "Mb/s", "mb/s", "Gb/s", "gb/s"]
            end_of_transfer = False
            if any(tm in pexp_match.decode("utf-8") for tm in tokens_to_match):
                tokens = pexp_match.decode("utf-8").split(" ")
                if 'ETA' in tokens:
                    pct_completed = [x for x in tokens if len(x) > 1 and x[-1] == '%']
                    if pct_completed:
                        output["pct_completed"] = pct_completed[0][:-1]

                        bytes_transferred = [x for x in tokens if len(x) > 2 and x[-2:] in units_to_match]
                        if bytes_transferred:
                            output["bytes_transferred"] = bytes_transferred[0]

                        transfer_rate = [x for x in tokens if len(x) > 4 and x[-4:] in rates_to_match]
                        if transfer_rate:
                            output["transfer_rate"] = transfer_rate[0]

                        output["url"] = url

                        if handler and callable(handler):
                            handler(json.dumps(output))
                        else:
                            sys.stdout.write("%s : %s%% transferred, %s, %s\n" % (output["url"], output["pct_completed"], output["bytes_transferred"], output["transfer_rate"]))
    thread.close()

def _do_aspera_transfer(cmd, handler):
    p = Popen(shlex.split(cmd),
              stdout=PIPE,
              stderr=STDOUT,
              bufsize=1)
    with p.stdout:
        for line in iter(p.stdout.readline, b''):
            if handler and callable(handler):
                handler(line)
            else:
                sys.stdout.write(line),
    p.wait()
    pass

def get_wgs_file_ext(output_format):
    if output_format == EMBL_FORMAT:
        return WGS_EMBL_EXT
    elif output_format == FASTA_FORMAT:
        return WGS_FASTA_EXT
    elif output_format == MASTER_FORMAT:
        return WGS_MASTER_EXT

def get_wgs_ftp_url(wgs_set, status, output_format):
    base_url = WGS_FTP_BASE + '/' + status + '/' + wgs_set[:2].lower() + '/' + wgs_set
    return base_url + get_wgs_file_ext(output_format)

def get_nonversioned_wgs_ftp_url(wgs_set, status, output_format):
    ftp_url = 'ftp.ebi.ac.uk'
    base_dir = WGS_FTP_DIR + '/' + status + '/' + wgs_set[:2].lower()
    base_url = WGS_FTP_BASE + '/' + status + '/' + wgs_set[:2].lower()
    ftp = ftplib.FTP(ftp_url)
    ftp.login()
    ftp.cwd(base_dir)
    supp = ftp.nlst()
    ftp.close()
    files = [f for f in supp if f.startswith(wgs_set) and f.endswith(get_wgs_file_ext(output_format))]
    if len(files) == 0:
        return None
    else:
        return base_url + '/' + max(files)

def get_report_from_portal(url):
    request = urllib2.Request(url)
    request.add_header('Authorization', b'Basic ' + base64.b64encode(ANON_USER + b':' + ANON_PWD))
    return urllib2.urlopen(request)

def download_report_from_portal(url, dest_file):
    response = get_report_from_portal(url)
    f = open(dest_file, 'w')
    for line in response:
        f.write(line)
    f.flush()
    f.close()

def get_accession_query(accession):
    query = 'query='
    if is_run(accession):
        query += 'run_accession="{0}"'.format(accession)
    elif is_experiment(accession):
        query += 'experiment_accession="{0}"'.format(accession)
    elif is_analysis(accession):
        query += 'analysis_accession="{0}"'.format(accession)
    return query

def get_ftp_file_fields(accession):
    fields = 'fields='
    fields += SUBMITTED_FIELD + ',' + SUBMITTED_MD5_FIELD
    if is_analysis(accession):
        return fields
    fields += ',' + INDEX_FIELD
    fields += ',' + SRA_FIELD + ',' + SRA_MD5_FIELD
    fields += ',' + FASTQ_FIELD + ',' + FASTQ_MD5_FIELD
    return fields

def get_aspera_file_fields(accession):
    fields = 'fields='
    fields += SUBMITTED_ASPERA_FIELD + ',' + SUBMITTED_MD5_FIELD
    if is_analysis(accession):
        return fields
    fields += ',' + INDEX_ASPERA_FIELD
    fields += ',' + SRA_ASPERA_FIELD + ',' + SRA_MD5_FIELD
    fields += ',' + FASTQ_ASPERA_FIELD + ',' + FASTQ_MD5_FIELD
    return fields

def get_file_fields(accession, aspera):
    if aspera:
        return get_aspera_file_fields(accession)
    else:
        return get_ftp_file_fields(accession)

def get_result(accession):
    if is_run(accession) or is_experiment(accession):
        return RUN_RESULT
    else:  # is_analysis(accession)
        return ANALYSIS_RESULT

def get_file_search_query(accession, aspera):
    return PORTAL_SEARCH_BASE + get_accession_query(accession) + '&' + \
        get_result(accession) + '&' + \
        get_file_fields(accession, aspera) + '&limit=0'

def split_filelist(filelist_string):
    if filelist_string.strip() == '':
        return []
    return filelist_string.strip().split(';')

def parse_file_search_result_line(line, accession, output_format):
    cols = line.split('\t')
    data_acc = cols[0].strip()
    sub_filelist = split_filelist(cols[1])
    sub_md5list = split_filelist(cols[2])
    if is_analysis(accession):
        return data_acc, sub_filelist, sub_md5list, []
    indexlist = split_filelist(cols[3])
    sra_filelist = split_filelist(cols[4])
    sra_md5list = split_filelist(cols[5])
    fastq_filelist = split_filelist(cols[6])
    fastq_md5list = split_filelist(cols[7])
    if (output_format is None and len(sub_filelist) > 0):
        output_format = SUBMITTED_FORMAT
    elif (output_format is None and len(sra_filelist) > 0):
        output_format = SRA_FORMAT
    elif output_format is None:
        output_format = FASTQ_FORMAT
    if output_format == SUBMITTED_FORMAT:
        return data_acc, sub_filelist, sub_md5list, indexlist
    if output_format == SRA_FORMAT:
        return data_acc, sra_filelist, sra_md5list, []
    return data_acc, fastq_filelist, fastq_md5list, []

def create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def get_group_query(accession, subtree):
    query='query='
    if is_primary_study(accession):
        query += 'study_accession="{0}"'.format(accession)
    elif is_secondary_study(accession):
        query += 'secondary_study_accession="{0}"'.format(accession)
    elif is_primary_sample(accession):
        query += 'sample_accession="{0}"'.format(accession)
    elif is_secondary_sample(accession):
        query += 'secondary_sample_accession="{0}"'.format(accession)
    elif is_taxid(accession):
        if subtree:
            query += 'tax_tree({0})'.format(accession)
        else:
            query += 'tax_eq({0})'.format(accession)
    return query

def get_group_fields(group):
    fields = 'fields='
    if group in [SEQUENCE, WGS, ASSEMBLY]:
        fields += 'accession'
    elif group == READ:
        fields += 'run_accession'
    elif group == ANALYSIS:
        fields += 'analysis_accession'
    return fields

def get_group_result(group):
    if group == READ:
        return RUN_RESULT
    elif group == ANALYSIS:
        return ANALYSIS_RESULT
    elif group == WGS:
        return WGS_RESULT
    elif group == ASSEMBLY:
        return ASSEMBLY_RESULT

def get_group_search_query(group, result, accession, subtree):
    return PORTAL_SEARCH_BASE + get_group_query(accession, subtree) + '&' \
        + result + '&' + get_group_fields(group) + '&limit=0'

def get_experiment_search_query(run_accession):
    return PORTAL_SEARCH_BASE + 'query=run_accession="' + run_accession + '"' \
        + '&result=read_run&fields=experiment_accession&limit=0'

def is_empty_dir(target_dir):
    for dirpath, dirnames, files in os.walk(target_dir):
        if files:
            return False
    return True

def print_error():
    sys.stderr.write('ERROR: Something unexpected went wrong please try again.\n')
    sys.stderr.write('If problem persists, please contact datasubs@ebi.ac.uk for assistance.\n')

def chunk_report(f, bytes_so_far, chunk_size, total_size, handler=None):
    global start_time
    if bytes_so_far == chunk_size:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(bytes_so_far)
    speed = int(progress_size / ((1024 * 1024) * duration))
    percent = int(progress_size * 100 /total_size)
    line = "\r%s: %0.f%%, %d MB, %d MB/s" % (f, percent, progress_size / (1024 * 1024), speed)
    
    if handler and callable(handler):
        handler(line)
    else:
        sys.stdout.write(line)

    if bytes_so_far >= total_size:
        if handler and callable(handler):
            handler('\n')
        else:
            sys.stdout.write('\n')

def chunk_read(response, file_handle, chunk_size=104857, tick_rate=10, report_hook=chunk_report, handler=None):
    total_size = response.info().getheader('Content-Length').strip()
    bytes_so_far = 0
    
    with open(file_handle, 'wb') as f:
        base = os.path.basename(file_handle)
        if total_size is None: # cannot chunk - no content length
            f.write(response.content)
        else:
            tick = 0
            total_size = int(total_size)
            while 1:
                chunk = response.read(chunk_size)
                bytes_so_far += len(chunk)

                if not chunk:
                    break

                f.write(chunk)
                
                if report_hook:
                    if tick == 0 or tick % int(tick_rate) == 0:
                        tick = 0
                        report_hook(base, bytes_so_far, chunk_size, total_size, handler)
                tick += 1

    return bytes_so_far

def get_divisor(record_cnt):
    if record_cnt <= 10000:
        return 1000
    elif record_cnt <= 50000:
        return 5000
    return 10000

def record_start_line(line, output_format):
    if output_format == FASTA_FORMAT:
        return line.startswith(b'>')
    elif output_format == EMBL_FORMAT:
        return line.startswith(b'ID  ')
    else:
        return False

def extract_acc_from_line(line, output_format):
    if output_format == FASTA_FORMAT:
        return line.split(b'|')[1]
    elif output_format == EMBL_FORMAT:
        return line.split()[1][:-1]
    else:
        return ''
