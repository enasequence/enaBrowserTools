# enaBrowserTools

enaBrowserTools is a set of scripts that interface with the ENA web services to download data from ENA easily, without any knowledge of scripting required.

# License

Copyright 2017 EMBL - European Bioinformatics Institute Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at: http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

# Installation and Setup

## Python installation

Both Python 2 and Python 3 scripts are available.  The Python 2 scripts can be found in the "python" folder, and the Python 3 scripts in the "python3" folder.   

To run these scripts you will need to have Python installed.  You can download either Python 2 or Python 3 from [here](https://www.python.org/downloads/). If you already have Python installed, you can find out which version when you start the python interpreter.  If using Python 2, we suggest you upgrade to the latest version if you don't already have it: 2.7.

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

If you wish to use Aspera to download read or analysis files, you will need to edit the utils.py script. You will minimally need to specify the location of ascp and the licence file on your computer. All available aspera settings that can be modified are located at the top of utils.py:

```
ASPERA_BIN = 'ascp' # ascp binary
ASPERA_PRIVATE_KEY = '/path/to/aspera_dsa.openssh' # ascp private key file
ASPERA_LICENSE = 'aspera-license' # ascp license file
ASPERA_OPTIONS = '' # set any extra aspera options
ASPERA_SPEED = '100M' # set aspera download speed
```

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
                  [-m] [-i] [-a] [-v]
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
                        read group: submitted (default), fastq and sra
                        formats. analysis group: submitted only. Default is
                        submitted
  -d DEST, --dest DEST  Destination directory (default is current running
                        directory)
  -w, --wgs             Download WGS set for each assembly if available
                        (default is false)
  -m, --meta            Download read or analysis XML in addition to data
                        files (default is false)
  -i, --index           Download CRAM index files with submitted CRAM files,
                        if any (default is false). This flag is ignored for
                        fastq and sra format options.
  -a, --aspera          Use the aspera command line client to download,
                        instead of FTP (default is false).
  -v, --version         show program's version number and exit
```

## enaGroupGet

This tool will allow you to download all data of a particular group (sequence, WGS, assembly, read or analysis) for a given sample or study accession. You can also download all sequence, WGS or assembly data for a given NCBI tax ID. When fetching data for a tax ID, the default is to only search for the specific tax ID, however you can use the subtree option to download the data associated with either the requested taxon or any of its subordinate taxa in the NCBI taxonomy tree.

Downloading read and analysis data by tax ID is currently disabled. We will be adding a data volume sanity check in place before we enable this functionality.

Usage of this tool is described below.  A new directory will be created using the provided accession as the name, and all data will be downloaded here. There will also be a separate subdirectory created for each assembly, run and analysis being fetched.  Note that unless a destination directory is provided, this group directory will be created in the directory from which you run the command.  

```
usage: enaGroupGet [-h] [-g {sequence,wgs,assembly,read,analysis}]
                   [-f {embl,fasta,submitted,fastq,sra}] [-d DEST] [-w] [-m]
                   [-i] [-a] [-t] [-v]
                   accession

Download data for a given study or sample

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
  -m, --meta            Download read or analysis XML in addition to data
                        files (default is false)
  -i, --index           Download CRAM index files with submitted CRAM files,
                        if any (default is false). This flag is ignored for
                        fastq and sra format options.
  -a, --aspera          Use the aspera command line client to download,
                        instead of FTP (default is false).
  -t, --subtree         Include subordinate taxa (taxon subtree) when querying
                        with NCBI tax ID (default is false)
  -v, --version         show program's version number and exit
```

# Problems

For any problems, please contact datasubs@ebi.ac.uk with 'enaBrowserTools' in your subject line.

We have had a couple of reports that the R2 FASTQ files are not always successfully downloading for paired runs. We have been unable to replicate this problem and have therefore exposed the error message to you should there be any download failure of read/analysis files via FTP or Aspera. If you get one of these errors, copy the error into your email to datasubs.
