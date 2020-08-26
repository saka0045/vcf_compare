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

Script to qsub and run depthOfCoverage on a sample directory analyzed by MGC

<DEFINE PARAMETERS>

Parameters:
	-i [required] Sample directory - full path to the sample directory
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
COVERAGE_SCRIPT="${SCRIPT_ROOT}/src/bash/depthOfCoverage.sh"
SAMPLEDIR=""
SAMPLE=""
BAM=""
OUTDIR=""
TARGET_REGION=""
DEPTHOFCOVERAGE=""
COVERAGE_THRESHOLD=""
CMD=""
QSUB=""

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

while getopts "hi:c:" OPTION

do
  case $OPTION in
    h) echo "${DOCS}" ; rm ${LOG_FILE} ; exit ;;
    i) SAMPLEDIR="${OPTARG}" ;;
    c) COVERAGE_THRESHOLD="${OPTARG}" ;;
    ?) echo "${DOCS}" ; rm ${LOG_FILE} ; exit ;;
  esac
done

# Check arguments
validateParm "SAMPLEDIR" "Please specify the option: i"
validateParm "COVERAGE_THRESHOLD" "Please specify the option: c"
validateDirectory "${SAMPLEDIR}"

# Get the sample name
SAMPLE=$(basename ${SAMPLEDIR})
logInfo "Processing sample directory: ${SAMPLEDIR}"
logInfo "Sample name: ${SAMPLE}"

# Get the path to the BAM
BAM="${SAMPLEDIR}/mgc/alignment/${SAMPLE}.bam"
validateFile "${BAM}"
logInfo "Input BAM: ${BAM}"

# Source the mgc.cfg to get the reference genome
MGC_CONFIG="${SAMPLEDIR}/ordered_service/pipeline/mgc/mgc.cfg"
validateFile "${MGC_CONFIG}"
logInfo "Sourcing ${MGC_CONFIG}"
CMD="source ${MGC_CONFIG}"
logInfo "Executing command: ${CMD}"
${CMD}

# Get the target.bed
TARGET_REGION="${SAMPLEDIR}/ordered_service/target.bed"
validateFile "${TARGET_REGION}"
logInfo "Target region: ${TARGET_REGION}"

# Check to see if DepthOfCoverage directory exists in SAMPLEDIR
OUTDIR="${SAMPLEDIR}/DepthOfCoverage"
if [[ -d "${OUTDIR}" ]]; then
    logInfo "The output directory ${OUTDIR} already exists, aborting script"
    exit 1
fi

# Create the output directory
logInfo "Making the output directory: ${OUTDIR}"
CMD="mkdir ${OUTDIR}"
logInfo "Executing command: ${CMD}"
${CMD}

# Qsub and execute the depthOfCoverage.sh script
QSUB_ARGS="-V -q sandbox.q -l h_vmem=50G -m a -M sakai.yuta@mayo.edu -N DepthOfCoverage -wd ${OUTDIR} \
-o /dlmp/sandbox/cgslIS/Yuta/logs -j y"
CMD="${QSUB} ${QSUB_ARGS} ${COVERAGE_SCRIPT} -s ${SAMPLE} -b ${BAM} -o ${OUTDIR} -r ${Ref} -t ${TARGET_REGION} \
-c ${COVERAGE_THRESHOLD}"