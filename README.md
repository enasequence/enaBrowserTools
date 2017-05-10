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

Download the latest release and extract it to the preferred location on our computer. You will now have the enaBrowserTools folder, containing both the python 2 and 3 option scripts.  If you are using a Unix/Linux or Mac computer, we suggest you add the following aliases to your .bashrc or .bash_profile file. Where INSTALLATION_DIR is the location where you have saved the enaBrowserTools to and PYTHON_CHOICE will depend on whether you are using the Python 2 or Python 3 scripts.

```
alias enaDataGet=INSTALLATION_DIR/enaBrowserTools/PYTHON_CHOICE/enaDataGet
alias enaGroupGet=INSTALLATION_DIR/enaBrowserTools/PYTHON_CHOICE/enaGroupGet
alias sequenceGet=INSTALLATION_DIR/enaBrowserTools/PYTHON_CHOICE/sequenceGet
alias assemblyGet=INSTALLATION_DIR/enaBrowserTools/PYTHON_CHOICE/assemblyGet
alias readGet=INSTALLATION_DIR/enaBrowserTools/PYTHON_CHOICE/readGet
alias analysisGet=INSTALLATION_DIR/enaBrowserTools/PYTHON_CHOICE/analysisGet
```

This will allow you to run the tools from any location on your computer.

We will aim to provide instructions and batch scripts for running these tools on Windows at a later date.

# Command line

There are two main tools for downloading data from ENA:  enaDataGet and enaGroupGet.  

## enaDataGet

This tool will download all data for a given sequence, assembly, read or analysis accession or WGS prefix (LLLLVV, eg CDHE01).  Usage of this tool is described below.  Note that unless a destination directory is provided, the data will be downloaded to the directory from which you run the command.

```
usage: enaDataGet [-h] [-f {embl,fasta,submitted,fastq,sra}] [-d DEST] [-w]
                  [-m] [-i] [-v]
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
  -v, --version         show program's version number and exit
```

To simplify the download of data, we also offer the component tools separately: sequenceGet, assemblyGet, readGet and analysisGet. Each of these also have the -h option to list the usage.

## enaGroupGet

This tool will allow you to download all data of a particular group (sequence, WGS, assembly, read or analysis) for a given sample or study accession. Usage of this tool is described below.  You will get a new directory using the provided accession as the directory name, and all data will be downloaded here.  Note that unless a destination directory is provided, this group directory will be created in the directory from which you run the command.  

```
usage: enaGroupGet [-h] [-g {sequence,wgs,assembly,read,analysis}]
                   [-f {embl,fasta,submitted,fastq,sra}] [-d DEST] [-w] [-m]
                   [-i] [-v]
                   accession

Download data for a given study or sample

positional arguments:
  accession             Study or sample accession to fetch data for

optional arguments:
  -h, --help            show this help message and exit
  -g {sequence,wgs,assembly,read,analysis}, --group {sequence,wgs,assembly,read,analysis}
                        Data group to be downloaded for this study/sample
                        (default is read)
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
  -v, --version         show program's version number and exit
```
