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

Script to filter out false positives and false negatives from MGC VCF

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
COMMON_FUNC=""
LOG_DIR=""
LOG_FILE=""
SAMPLE=""
HAPPY_FP_VCF=""
HAPPY_FN_VCF=""
GREP=""
CMD=""
HAPPY_DIR=""
FP_COORDINATES=""
FN_COORDINATES=""
AF_FILTERED_MGC_VCF=""
FP_FILTERED_MGC_VCF=""
FN_FILTERED_MGC_VCF=""
CLC_VCF=""
ZGREP=""

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

while getopts "hi:" OPTION

do
  case $OPTION in
    h) echo "${DOCS}" ; rm ${LOG_FILE} ; exit ;;
    i) SAMPLEDIR="${OPTARG}" ;;
    ?) echo "${DOCS}" ; rm ${LOG_FILE} ; exit ;;
  esac
done

# Check arguments
validateParm "SAMPLEDIR" "Please specify the option: i"
validateDirectory "${SAMPLEDIR}"

# Remove any trailing "/" from SAMPLEDIR
SAMPLEDIR=${SAMPLEDIR%/}

# Get the sample name
SAMPLE=$(basename ${SAMPLEDIR})
logInfo "Processing directory: ${SAMPLEDIR}"
logInfo "Sample Name: ${SAMPLE}"

# Check files exists
HAPPY_FP_VCF="${HAPPY_DIR}/${SAMPLE}_CLC_MGC_false_positives.vcf"
HAPPY_FN_VCF="${HAPPY_DIR}/${SAMPLE}_CLC_MGC_false_negatives.vcf"
AF_FILTERED_MGC_VCF="${SAMPLEDIR}/mgc/reports/${SAMPLE}_filtered.vcf"
CLC_VCF="${SAMPLEDIR}/${SAMPLE}_final.vcf.gz"
validateFile "${HAPPY_FP_VCF}"
validateFile "${HAPPY_FN_VCF}"
validateFile "${AF_FILTERED_MGC_VCF}"
validateFile "${CLC_VCF}"


# Grep the coordinates from hap.py FP VCF
HAPPY_DIR="${SAMPLEDIR}/hap.py_out"
FP_COORDINATES="${HAPPY_DIR}/${SAMPLE}_CLC_MGC_false_positives_coordinates"
CMD="${GREP} -v \"^#\" ${HAPPY_FP_VCF} | cut -f2 > ${FP_COORDINATES}"
logInfo "Executing command: ${CMD}"
eval ${CMD}

# Grep the coordinates from hap.py FN VCF
FN_COORDINATES="${HAPPY_DIR}/${SAMPLE}_CLC_MGC_false_negatives_coordinates"
CMD="${GREP} -v \"^#\" ${HAPPY_FN_VCF} | cut -f2 > ${FN_COORDINATES}"
logInfo "Executing command: ${CMD}"
eval ${CMD}

# Filter the MGC VCF to the false positives
FP_FILTERED_MGC_VCF="${SAMPLEDIR}/${SAMPLE}_MGC_false_positives.vcf"
CMD="${GREP} \"^#\" ${AF_FILTERED_MGC_VCF} > ${FP_FILTERED_MGC_VCF}"
logInfo "Executing command: ${CMD}"
eval ${CMD}
CMD="${GREP} -f ${FP_COORDINATES} ${AF_FILTERED_MGC_VCF} >> ${FP_FILTERED_MGC_VCF}"
logInfo "Executing command: ${CMD}"
eval ${CMD}

# Filter the MGC VCF to the false negatives
FN_FILTERED_MGC_VCF="${SAMPLEDIR}/${SAMPLE}_CLC_false_negatives.vcf"
CMD="${ZGREP} \"^#\" ${CLC_VCF} > ${FN_FILTERED_MGC_VCF}"
logInfo "Executing command: ${CMD}"
eval ${CMD}
CMD="${ZGREP} -f ${FN_COORDINATES} ${CLC_VCF} >> ${FN_FILTERED_MGC_VCF}"
logInfo "Executing command: ${CMD}"
eval ${CMD}

logInfo "Script is done running"