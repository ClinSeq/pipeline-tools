#!/bin/bash

PROJECT=
FORCE=
REMOTEUSER=${USER}

usage()
{
echo "
usage: $0 options

This scropt transfer a project to grond. If the given project 
name already exists there, the flag -f is needed to force sync. 

The script uses rsync to sync files to grond.

Options:

 -p remote project id
 -s /path/to/project
 -f Force sync
 -r Remote user name ($HOST if unset)

"
}

SOURCEDIR=

while getopts "hfp:r:s:" OPTION
do
    case ${OPTION} in
	h)
	    usage
	    exit 1
	    ;;
	f)
	    FORCE="YES"
	    ;;
	p)
	    PROJECT=$OPTARG
	    ;;
	r)
	    REMOTEUSER=$OPTARG
	    ;;
	s)
	    SOURCEDIR=$OPTARG
	    ;;
    esac
done

TARGETDIR=/home/Crisp/clinseq/${PROJECT}

if [[ -z "$PROJECT" ]]
then
    echo "ERROR: PROJECT not set."
    usage
    exit 1
fi

if [[ -z "$SOURCEDIR" ]]
then
    echo "ERROR: SOURCEDIR not set."
    usage
    exit 1
fi

if [ ! -d ${SOURCEDIR} ]; then
    echo "Source dir $SOURCEDIR does not exist."
    usage
    exit 1
fi

## function to perform the sync
do_sync(){
    
    XSOURCEDIR=$1
    XTARGETDIR=$2

    cd ${XSOURCEDIR}
    ssh ${REMOTEUSER}@grond.scilifelab.se "mkdir -p ${XTARGETDIR}"
    RSYNC="rsync -e ssh -av --progress --files-from=- . ${REMOTEUSER}@grond.scilifelab.se:${XTARGETDIR}"

    ## transfer report files
    find .|grep report$| ${RSYNC}

    ## transfer contents of reports
    for REPORTFILE in `find .|grep report$`; do
	DIR=`dirname ${REPORTFILE}`/
	grep -v REPORTID ${REPORTFILE} | cut -f 11- | tr "\t" "\n"|grep -v "^NA$"| awk -v DIR=$DIR '{print DIR$0}' |$RSYNC
    done
   
}


echo "## Transferring project to grond. Parameters: "
echo "REMOTEUSER=$REMOTEUSER"
echo "FORCE=$FORCE"
echo "SOURCEDIR=$SOURCEDIR"
echo "TARGETDIR=$TARGETDIR"
echo

## If target folder exists, -f(orce) flag is needed to sync
if ( ssh ${REMOTEUSER}@grond.scilifelab.se "[ -d ${TARGETDIR} ]" )
then
    if [[ -n ${FORCE} ]]
    then
	echo "TARGET $TARGETDIR exists, but -f is set so syncing anyway."
	do_sync ${SOURCEDIR} ${TARGETDIR}
    else
	echo "TARGET $TARGETDIR EXISTS. Must use -f to sync anyway"
    fi
else
    echo "Syncing reports, from ${SOURCEDIR} to grond:${TARGETDIR}"
    do_sync ${SOURCEDIR} ${TARGETDIR}
fi

exit 0