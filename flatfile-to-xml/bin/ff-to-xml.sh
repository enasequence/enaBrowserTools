#!/bin/bash
if [ $# -eq 3 ]
then
    java -jar flatfile-to-xml-1.0.0.jar --flatfile="$1" --xmlfile="$2" --format="$3"
    exit $?
fi

if [ $# -eq 2 ]
then
    java -jar flatfile-to-xml-1.0.0.jar --flatfile="$1" --xmlfile="$2"
    exit $?
fi

if [ $# -lt 2 ]
then
    echo "Usage: <flatfile path> <xml output path> <flatfile format: EMBL/CDS/NCR/MASTER>"
    echo "Last argument is optional. Default format is EMBL."
    echo "e.g."
    echo "./ff-to-xml.sh c:\user\ABC.txt c:\user\ABC.xml CDS"
fi

