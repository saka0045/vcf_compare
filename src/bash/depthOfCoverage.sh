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

Script to run DepthOfCoverage

<DEFINE PARAMETERS>

Parameters:
	-i [required] Sample directory - full path to the sample directory
	-b [required] Input BAM - full path to sample's input BAM
	-o [required] Output directory - full path to the output directory to save results
	-r [required] Reference genome - full path to the reference genome fasta file
	-t [required] Target region - full path to the target region BED file
	-c [required] Coverage threshold - coverage threshold to use for the summary file
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
PYTHON_SCRIPT_DIR="${SCRIPT_ROOT}/src/python"
SAMPLE=""
BAM=""
OUTDIR=""
REFERENCE=""
TARGET_REGION=""
DEPTHOFCOVERAGE=""
COVERAGE_THRESHOLD=""
CMD=""

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

while getopts "hi:b:o:r:t:c:" OPTION

do
  case $OPTION in
    h) echo "${DOCS}" ; rm ${LOG_FILE} ; exit ;;
    i) SAMPLEDIR="${OPTARG}" ;;
    b) BAM="${OPTARG}" ;;
    o) OUTDIR="${OPTARG}" ;;
    r) REFERENCE="${OPTARG}" ;;
    t) TARGET_REGION="${OPTARG}" ;;
    c) COVERAGE_THRESHOLD="${OPTARG}" ;;
    ?) echo "${DOCS}" ; rm ${LOG_FILE} ; exit ;;
  esac
done

# Check arguments
validateParm "SAMPLEDIR" "Please specify the option: i"
validateParm "BAM" "Please specify the option: b"
validateParm "OUTDIR" "Please specify the option: o"
validateParm "REFERENCE" "Please specify the option: r"
validateParm "TARGET_REGION" "Please specify the option: t"
validateParm "COVERAGE_THRESHOLD" "Please specify the option: c"
validateDirectory "${SAMPLEDIR}"
validateFile "${BAM}"
validateDirectory "${OUTDIR}"
validateFile "${REFERENCE}"
validateFile "${TARGET_REGION}"

# Remove any trailing "/" from SAMPLEDIR
SAMPLEDIR=${SAMPLEDIR%/}

# Get the sample name
SAMPLE=$(basename ${SAMPLEDIR})
logInfo "Sample Name: ${SAMPLE}"
logInfo "Reference genome: ${REFERENCE}"
logInfo "Target region: ${TARGET_REGION}"
logInfo "Using coverage threshold: ${COVERAGE_THRESHOLD}"
logInfo "Saving results to: ${OUTDIR}"

CMD="${DEPTHOFCOVERAGE} --input ${BAM} -L ${TARGET_REGION} -O ${OUTDIR}/${SAMPLE} -R ${REFERENCE} \
--summary-coverage-threshold ${COVERAGE_THRESHOLD}"

logInfo "Executing command: ${CMD}"
${CMD}