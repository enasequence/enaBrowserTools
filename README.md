# enaBrowserTools

enaBrowserTools is a set of scripts that interface with the ENA web services to download data from ENA easily, without any knowledge of scripting required.

*Important: Please note that v1.5.4 is the last update that will support python 2.7. Due to the 2019 scheduled retirement of python 2.7, the next release (2.0) will be restructured to hold only python 3 scripts.*

# License

Copyright 2017 EMBL - European Bioinformatics Institute Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at: http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

# Installation and Setup

## Python installation

Both Python 2 and Python 3 scripts are available.  The Python 2 scripts can be found in the "python" folder, and the Python 3 scripts in the "python3" folder.   

To run these scripts you will need to have Python installed.  You can download either Python 2 or Python 3 from [here](https://www.python.org/downloads/). If you already have Python installed, you can find out which version when you start the python interpreter.  If using Python 2, we suggest you upgrade to the latest version if you don't already have it: 2.7.

Note that EBI now uses HTTPS servers. This can create a problem when using Python 3 on a Mac due to an oft-missed
installation step. Please run the "Install Certificates.command" command to ensure your Python 3 installation on
the Mac can correctly authenticate against the servers. To do this, run the following from a terminal window, updating
the Python version with the correct version of Python 3 that you have installed:
open "/Applications/Python 3.6/Install Certificates.command"

We have had a report from a user than when Python 3 was installed using homebrew, the following code needed to be run instead:
```
# install_certifi.py
#
# sample script to install or update a set of default Root Certificates
# for the ssl module.  Uses the certificates provided by the certifi package:
#       https://pypi.python.org/pypi/certifi

import os
import os.path
import ssl
import stat
import subprocess
import sys

STAT_0o775 = ( stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
             | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP
             | stat.S_IROTH |                stat.S_IXOTH )

openssl_dir, openssl_cafile = os.path.split(
    ssl.get_default_verify_paths().openssl_cafile)

print(" -- pip install --upgrade certifi")
subprocess.check_call([sys.executable,
    "-E", "-s", "-m", "pip", "install", "--upgrade", "certifi"])

import certifi

# change working directory to the default SSL directory
os.chdir(openssl_dir)
relpath_to_certifi_cafile = os.path.relpath(certifi.where())
print(" -- removing any existing file or link")
try:
    os.remove(openssl_cafile)
except FileNotFoundError:
    pass
print(" -- creating symlink to certifi certificate bundle")
os.symlink(relpath_to_certifi_cafile, openssl_cafile)
print(" -- setting permissions")
os.chmod(openssl_cafile, STAT_0o775)
print(" -- update complete")
```

## Installing and running the scripts

Download the [latest release](https://github.com/enasequence/enaBrowserTools/releases/latest) and extract it to the preferred location on your computer. You will now have the enaBrowserTools folder, containing both the python 2 and 3 option scripts.  If you are using a Unix/Linux or Mac computer, we suggest you add the following aliases to your .bashrc or .bash_profile file. Where INSTALLATION_DIR is the location where you have saved the enaBrowserTools to and PYTHON_CHOICE will depend on whether you are using the Python 2 or Python 3 scripts.

```
alias enaDataGet=INSTALLATION_DIR/enaBrowserTools/PYTHON_CHOICE/enaDataGet
alias enaGroupGet=INSTALLATION_DIR/enaBrowserTools/PYTHON_CHOICE/enaGroupGet
```

This will allow you to run the tools from any location on your computer.

You can run install and run these scripts on Windows as you would in Unix/Linux using [Cygwin](https://cygwin.com). If you have python installed on your Windows machine, you can run the python scripts directly without Cygwin. However the call is a bit more complicated.

For example, instead of calling ```enaDataGet```

you would need to call ```python INSTALLATION_DIR/enaBrowserTools/PYTHON_CHOICE/enaDataGet.py```

We will look more into the Windows equivalent of aliases to run batch files from the command line and hopefully be able to provide a better solution to Windows users shortly.

## Setting up for Aspera

*Important: there has been a change to using aspera in version 1.4.*

If you wish to use Aspera to download read or analysis files, you will need to use the aspera_settings.ini file.  Please save it to a static location on your local computer, and edit the file to include the location of your aspera binary (ASPERA_BIN) and the private key file (ASPERA_PRIVATE_KEY):

```
[aspera]
ASPERA_BIN = /path/to/ascp
ASPERA_PRIVATE_KEY = /path/to/aspera_dsa.openssh
ASPERA_OPTIONS =
ASPERA_SPEED = 100M
```

There are two command line flags/options available if you wish to use aspera for download. These are:
1. -a (or --aspera): use this flag if you'd like to download with aspera.
2. -as (or --aspera-settings): use this option if you'd like to specify the location of your aspera settings file. If you use this option, you don't need to use the --aspera flag.

If you use the --aspera-settings option, you don't need to also use the --aspera flag, e.g:

```
enaDataGet -f fastq -as /path/to/aspera_settings.ini ACCESSION
```

If you don't wish to specify the location of the aspera settings file each time you use the scripts, you have the option to either set an ENA_ASPERA_INIFILE environment variable to save the location:

```
export ENA_ASPERA_INIFILE="/path/to/aspera_settings.ini"
```

or you can use the default location for the file, this is the enaBrowserTools directory.  Note that if you use this option, you will have to be careful about how you update your scripts so that you don't overwrite your aspera settings file.

Using just the --aspera flag will result in the scripts looking first for the ENA_ASPERA_INIFILE environment variable, and second for the default file location.

```
enaDataGet -f fastq -a ACCESSION
```

Regardless of which option you have selected, if the aspera settings file cannot be found or the licence key file declared within your settings file does not exist, the scripts will default to using FTP for the download.

# Command line

There are two main tools for downloading data from ENA:  enaDataGet and enaGroupGet.  

## enaDataGet

This tool will download all data for a given sequence, assembly, read or analysis accession or WGS set.  Usage of this tool is described below.  Note that unless a destination directory is provided, the data will be downloaded to the directory from which you run the command. When using an assembly, run, experiment or analysis accession, a subdirectory will be created using that accession as its name.

Accepted WGS set accession formats are:
- AAAK03
- AAAK03000000
- AAAK
- AAAK00000000

```
usage: enaDataGet [-h] [-f {embl,fasta,submitted,fastq,sra}] [-d DEST] [-w]
                  [-m] [-i] [-a] [-as ASPERA_SETTINGS] [-v]
                  accession

Download data for a given accession

positional arguments:
  accession             Sequence, coding, assembly, run, experiment or
                        analysis accession or WGS prefix (LLLLVV) to download

optional arguments:
  -h, --help            show this help message and exit
  -f {embl,fasta,submitted,fastq,sra}, --format {embl,fasta,submitted,fastq,sra}
                        File format required. Format requested must be
                        permitted for data type selected. sequence, assembly
                        and wgs accessions: embl(default) and fasta formats.
                        read group: submitted, fastq and sra formats. analysis
                        group: submitted only.
  -d DEST, --dest DEST  Destination directory (default is current running
                        directory)
  -w, --wgs             Download WGS set for each assembly if available
                        (default is false)
  -e, --extract-wgs     Extract WGS scaffolds for each assembly if available
                        (default is false)
  -exp, --expanded      Expand CON scaffolds when downloading embl format
                        (default is false)
  -m, --meta            Download read or analysis XML in addition to data
                        files (default is false)
  -i, --index           Download CRAM index files with submitted CRAM files,
                        if any (default is false). This flag is ignored for
                        fastq and sra format options.
  -a, --aspera          Use the aspera command line client to download,
                        instead of FTP.
  -as ASPERA_SETTINGS, --aspera-settings ASPERA_SETTINGS
                        Use the provided settings file, will otherwise check
                        for environment variable or default settings file
                        location.
  -v, --version         show program's version number and exit
```

## enaGroupGet

This tool will allow you to download all data of a particular group (sequence, WGS, assembly, read or analysis) for a given sample or study accession. You can also download all sequence, WGS or assembly data for a given NCBI tax ID. When fetching data for a tax ID, the default is to only search for the specific tax ID, however you can use the subtree option to download the data associated with either the requested taxon or any of its subordinate taxa in the NCBI taxonomy tree.

Downloading read and analysis data by tax ID is currently disabled. We will be adding a data volume sanity check in place before we enable this functionality.

Usage of this tool is described below.  A new directory will be created using the provided accession as the name, and all data will be downloaded here. There will also be a separate subdirectory created for each assembly, run and analysis being fetched.  Note that unless a destination directory is provided, this group directory will be created in the directory from which you run the command.  

```
usage: enaGroupGet [-h] [-g {sequence,wgs,assembly,read,analysis}]
                   [-f {embl,fasta,submitted,fastq,sra}] [-d DEST] [-w] [-m]
                   [-i] [-a] [-as ASPERA_SETTINGS] [-t] [-v]
                   accession

Download data for a given study or sample, or (for sequence and assembly) taxon

positional arguments:
  accession             Study or sample accession or NCBI tax ID to fetch data
                        for

optional arguments:
  -h, --help            show this help message and exit
  -g {sequence,wgs,assembly,read,analysis}, --group {sequence,wgs,assembly,read,analysis}
                        Data group to be downloaded for this
                        study/sample/taxon (default is read)
  -f {embl,fasta,submitted,fastq,sra}, --format {embl,fasta,submitted,fastq,sra}
                        File format required. Format requested must be
                        permitted for data group selected. sequence, assembly
                        and wgs groups: embl and fasta formats. read group:
                        submitted, fastq and sra formats. analysis group:
                        submitted only.
  -d DEST, --dest DEST  Destination directory (default is current running
                        directory)
  -w, --wgs             Download WGS set for each assembly if available
                        (default is false)
  -e, --extract-wgs     Extract WGS scaffolds for each assembly if available
                        (default is false)
  -exp, --expanded      Expand CON scaffolds when downloading embl format
                        (default is false)
  -m, --meta            Download read or analysis XML in addition to data
                        files (default is false)
  -i, --index           Download CRAM index files with submitted CRAM files,
                        if any (default is false). This flag is ignored for
                        fastq and sra format options.
  -a, --aspera          Use the aspera command line client to download,
                        instead of FTP.
  -as ASPERA_SETTINGS, --aspera-settings ASPERA_SETTINGS
                        Use the provided settings file, will otherwise check
                        for environment variable or default settings file
                        location.
  -t, --subtree         Include subordinate taxa (taxon subtree) when querying
                        with NCBI tax ID (default is false)
  -v, --version         show program's version number and exit
```

# Tips

From version 1.4, when downloading read data if you use the default format (that is, don't use the format option), the scripts will look for available files in the following priority: submitted, sra, fastq.

A word of advice for read formats:
- submitted: only read data submitted to ENA have files available as submitted by the user.
- sra:  this is the NCBI SRA format, and is the format in which all NCBI/DDBJ data is mirrored to ENA.
- fastq:  not all submitted format files can be converted to FASTQ

# Problems

For any problems, please contact datasubs@ebi.ac.uk with 'enaBrowserTools' in your subject line.

We have had a couple of reports that the R2 FASTQ files are not always successfully downloading for paired runs. We have been unable to replicate this problem and have therefore exposed the error message to you should there be any download failure of read/analysis files via FTP or Aspera. If you get one of these errors, please copy the error into your email to datasubs.
