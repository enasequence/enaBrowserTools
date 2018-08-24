@echo off
IF "%~1"=="" GOTO noargs
IF "%~2"=="" GOTO noargs
IF "%~3"=="" GOTO defaultformat

java -jar flatfile-to-xml-1.0.0.jar --flatfile="%1" --xmlfile="%2" --format="%3"
if errorlevel 1 (
   echo Exited with error code %errorlevel%
   exit /b %errorlevel%
)
GOTO :end

:noargs
echo Usage: "<flatfile path> <xml output path> <flatfile format: EMBL/CDS/NCR/MASTER>"
echo Last argument is optional. Default format is EMBL.
echo e.g.
echo ff-to-xml.cmd c:\user\ABC.txt c:\user\ABC.xml CDS
exit 1

:defaultformat
java -jar flatfile-to-xml-1.0.0.jar --flatfile="%1" --xmlfile="%2"
if errorlevel 1 (
   echo Exited with error code %errorlevel%
   exit /b %errorlevel%
)

:end


