#!/bin/bash

##################################################
# MANIFEST
##################################################

read -r -d '' MANIFEST <<MANIFEST

*******************************************
`readlink -m $0` ${@}
was called by: `whoami` on `date`
*******************************************

MANIFEST

echo "${MANIFEST}"

read -r -d '' DOCS <<DOCS

Script to compare the CLC and MGC TNhaplotyper2 VCFs using hap.py

<DEFINE PARAMETERS>

Parameters:
	-i [required] Sample directory - full path to the sample directory
	-h [optional] debug - option to print this menu option

Usage:
$0 -i {inputDirectory}
DOCS

#Show help when no parameters are provided
if [ $# -eq 0 ];
then
    echo "${DOCS}" ; exit 1 ;
fi

##################################################
#GLOBAL VARIABLES
##################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_FILE="${SCRIPT_DIR}/$(basename "${BASH_SOURCE[0]}")"
SCRIPT_NAME="$(basename ${0})"
SCRIPT_ROOT="$(cd "${SCRIPT_DIR}/../../" && pwd)"
PROFILE="${SCRIPT_ROOT}/config/compareVcf.profile"
SAMPLEDIR=""

##################################################
#Source Pipeline Profile
##################################################

echo "Using configuration file at ${PROFILE}"
source ${PROFILE}

##################################################
#Source Common Function
##################################################

if [[ ! -f ${COMMON_FUNC} ]]; then
    echo -e "\nERROR: The common functions were not found in ${COMMON_FUNC}\n"
    exit 1
fi

echo "Using common functions: ${COMMON_FUNC}"
source ${COMMON_FUNC}

##################################################
#Setup Logging
##################################################

setupLogging "${LOG_DIR}" "${SCRIPT_NAME}.log_$$" all

echo "${MANIFEST}" >> "${LOG_FILE}"

##################################################
#Bash handling
##################################################

set -o errexit
set -o pipefail
set -o nounset

##################################################
#BEGIN PROCESSING
##################################################

while getopts "hdi:s:" OPTION

do
  case $OPTION in
    h) echo "${DOCS}" ; rm ${LOG_FILE} ; exit ;;
    d) DEBUG="-d" ; set -x ;;
    i) SAMPLEDIR="${OPTARG}" ;;
    s) SAMPLE="${OPTARG}" ;;
    ?) echo "${DOCS}" ; rm ${LOG_FILE} ; exit ;;
  esac
done