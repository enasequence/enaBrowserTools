# License

Copyright 2017 EMBL - European Bioinformatics Institute Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at: http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.


# ENA brokers activities reporting script

broker_activity_reporter is a script designed to report on the monthly activity of a ENA
broker for a given data type. Currently supported data types are:
 - Analysis
 - Sample
 - Project/Study
 - Sequence
 - Assembly
 - Submission
 - Run
 - Experiment


# Installation 

### Retrieving the broker_activity_reporter docker version
Retrieve the docker version from the Github to launch the docker version of the broker_reporter script.

Clone this repository:
```
git clone <repo>
```

## Install dependencies
```
pip install cx_Oracle
pip install pandas 
pip install alive_progress
```
To run the broker_activity_reporter script.
inspect its help page

```
broker_activity_reporter.py --help
usage: broker_activity_reporter.py [-h] -d DATA_TYPE -b BROKER_NAME
                                   [-s [STATUS [STATUS ...]]] [-v]
                                   [-t [ANALYSIS_TYPE [ANALYSIS_TYPE ...]]]

Report on a Broker monthly data type submission activity

optional arguments:
  -h, --help            show this help message and exit
  -d DATA_TYPE, --data_type DATA_TYPE
                        Please provide the data type to report on
                        [analysis|sample|experiment|submission|runs|studies|]
  -b BROKER_NAME, --broker_name BROKER_NAME
                        Provide the broker name example [ArrayExpress|EBI-
                        EMG]or provide three or more character for a greedy
                        search
  -s [STATUS [STATUS ...]], --status [STATUS [STATUS ...]]
                        Space separated data type status a combination of the 
                        following:[draft|private|cancelled|public|suppressed|k
                        illed],default[draft,private,public]
  -v, --verbose         Increase processing verbosity
  -t [ANALYSIS_TYPE [ANALYSIS_TYPE ...]], --analysis_type [ANALYSIS_TYPE [ANALYSIS_TYPE ...]]
                        Report on specific analysis type. A space separate
                        analysis type, a combination of the following:[SEQUENC
                        E_VARIATION|PROCESSED_READS|GENOME_MAP|SEQUENCE_ASSEMB
                        LY|TRANSCRIPTOME_ASSEMBLY|AMR_ANTIBIOGRAM|SAMPLE_PHENO
                        TYPE|PATHOGEN_ANALYSIS|TAXONOMIC_REFERENCE_SET|SEQUENC
                        E_FLATFILE|REFERENCE_ALIGNMENT|REFERENCE_SEQUENCE|SEQU
                        ENCE_ANNOTATION]

```
### Usage
Report on the data type analysis the monthly activity of ArrayExpress broker

```
./broker_activity_reporter.py  --data_type analysis --broker_name arrayexpress
|██████████████████████████▋⚠            | (!) 2/3 [67%] in 0.3s (7.79/s) 
  BROKER_NAME CENTER_NAME  COUNT CREATED_FIRST DATA_TYPE STATUS_ID SUBMISSION_ACCOUNT_ID
 ArrayExpress         EBI     37       03-2013  ANALYSIS    public              Webin-24
 ArrayExpress         EBI      6       04-2013  ANALYSIS    public              Webin-24
```