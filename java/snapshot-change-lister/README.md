# ENA Flatfile Snapshot Change Lister

This tool can be run periodically to get a comprehensive list of changes that occurred
within the public set of a given type's (Sequence/Coding/Non-Coding RNA) nucelotide sequence flatfiles.

# License

Copyright 2021 EMBL - European Bioinformatics Institute Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at: http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

# Functionality

1. This program downloads the complete list of public INSDC sequence accessions and their last updated dates (if available) for the requested type using the ENA Portal API.
e.g. for sequence:
https://www.ebi.ac.uk/ena/portal/api/search?dataPortal=ena&result=sequence&limit=0&fields=accession,last_updated

2. It then compares the new list against a previous list of the same type and generates 2 lists.
    list of new or updated records since the last time
    list of suppressed/killed records since the last time

# Installation and Setup

Download the latest release from the github releases.
Java runtime version 8 or higher is required.

# Running the program

You need to provide 3 arguments.

1. dataType : SEQUENCE/CODING/NONCODING
   
2. previousSnapshot : Local filepath to the previous complete report downloaded by this program. If this is the 1st time
   you're running the program, create a blank text file and provide it's path.
   
3. outputLocation : Local folder where the new complete report and the 2 change lists are to be created. Ensure there's
    enough disk space available.
    
4. email : optionally provide an email address to be notified when the process is complete

5. query : optionally provide a query string to filter the contents of your snapshot. Use the Query page in the 
   https://www.ebi.ac.uk/ena/browser/advanced-search wizard to build up the query. This should be the same query 
   for every execution of the tool for a specific snapshot. e.g. --query=dataclass="CON"

6. downloadData : (Optional) If value is true, the tool will also fetch the data for the new/updated records and save 
   them in a .dat file.

7. format : (Optional) Used only if downloadData=true. Request embl flatfile format (default) or fasta format for
   downloaded data.

8. annotationOnly : (Optional) Used only if downloadData=true and format=embl. Download only the annotations, excluding
   sequence lines.

e.g. 1
java -jar [path]/snapshot-change-lister-1.1.0.jar --dataType=CODING --previousSnapshot=[path]/coding_20210701.tsv --outputLocation=[path] --email=email@email.com

If this program were run on 2021-08-03, it would create 3 new files in the outputLocation folder.

coding_20210803.tsv

coding_20210803_new-or-updated.tsv

coding_20210803_deleted.tsv

e.g. 2
java -jar [path]/snapshot-change-lister-1.1.0.jar --dataType=SEQUENCE --previousSnapshot=[path]/sequence_20220220.tsv --outputLocation=[path] --query=dataclass="HTG" --downloadData=true --format=embl --annotationOnly=true"

If this program were run on 2022-02-23, it would create 4 new files in the outputLocation folder.

sequence_20220223.tsv

sequence_20220223_new-or-updated.tsv

sequence_20220223_new-or-updated.dat

sequence_20220223_deleted.tsv


Example for running in LSF:

bsub -n 2 -M 10000 -J coding-snapshot-change-lister -o /path/snapshot-changes/output-20211210.log java -jar  snapshot-change-lister-1.0.0.jar --email=email@email.com --dataType=CODING --previousSnapshot=/path/coding_20211028.tsv --outputLocation=/path/



# Support

Direct any questions/issues to https://www.ebi.ac.uk/ena/browser/support with snapshot-change-lister in the subject
