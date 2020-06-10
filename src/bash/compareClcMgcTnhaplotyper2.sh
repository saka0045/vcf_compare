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
COMMON_FUNC=""
LOG_DIR=""
LOG_FILE=""
SAMPLE=""
CLC_VCF=""
BGZIP=""
TABIX=""
CMD=""
MGC_VCF=""
BCFTOOLS=""
FILTERED_MGC_VCF=""
PYTHON2710=""
HAPPY_DIR=""
HAPPY=""
REF_GENOME=""
HAPPY_ARGS=""
FP_VCF=""
FN_VCF=""
HAPPY_VCF=""

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
CLC_VCF="${SAMPLEDIR}/${SAMPLE}_cmb.vcf.gz"
MGC_VCF="${SAMPLEDIR}/mgc/reports/${SAMPLE}.vcf"
validateFile "${CLC_VCF}"
validateFile "${MGC_VCF}"

# Source python 2.7.10
logInfo "Sourcing python 2.7.10"
CMD="source ${PYTHON2710}"
logInfo "Executing command: ${CMD}"
eval ${CMD}

# bgzip and tabix the original CLC VCF
logInfo "bgzipping the original CLC VCF: ${SAMPLEDIR}/${SAMPLE}_cmb.vcf"
CMD="${BGZIP} ${SAMPLEDIR}/${SAMPLE}_cmb.vcf"
logInfo "Executing command: ${CMD}"
eval ${CMD}
logInfo "tabix-ing the bgzipped CLC VCF: ${CLC_VCF}"
CMD="${TABIX} -p vcf ${CLC_VCF}"
logInfo "Executing command: ${CMD}"
eval ${CMD}

# Filter the "strand_artifact" variants from MGC VCF
logInfo "Filtering strand_artifact variants from MGC VCF: ${MGC_VCF}"
FILTERED_MGC_VCF="${SAMPLEDIR}/mgc/reports/${SAMPLE}_filtered.vcf"
CMD="${BCFTOOLS} view -e 'FILTER=\"strand_artifact\"' ${MGC_VCF} > ${FILTERED_MGC_VCF}"
logInfo "Executing command: ${CMD}"
eval ${CMD}

# Run hap.py
HAPPY_DIR="${SAMPLEDIR}/hap.py_out"
logInfo "Creating output directory for hap.py: ${HAPPY_DIR}"
CMD="mkdir ${HAPPY_DIR}"
logInfo "Executing command: ${CMD}"
eval ${CMD}
logInfo "Running hap.py to compare CLC and filtered MGC VCF"
HAPPY_ARGS="-o ${HAPPY_DIR}/${SAMPLE}_CLC_MGC -r ${REF_GENOME} --engine=scmp-somatic"
CMD="${HAPPY} ${CLC_VCF} ${FILTERED_MGC_VCF} ${HAPPY_ARGS}"
logInfo "Executing command: ${CMD}"
eval ${CMD}

# Separate the false positives and false negatives in separate VCF files
logInfo "Creating VCF files for false positives and false negatives"
FP_VCF="${HAPPY_DIR}/${SAMPLE}_CLC_MGC_false_positives.vcf"
FN_VCF="${HAPPY_DIR}/${SAMPLE}_CLC_MGC_false_negatives.vcf"
HAPPY_VCF="${HAPPY_DIR}/${SAMPLE}_CLC_MGC.vcf.gz"
CMD="${BCFTOOLS} view -i 'FORMAT/BD=\"FP\"' ${HAPPY_VCF} > ${FP_VCF}"
logInfo "Executing command: ${CMD}"
eval ${CMD}
CMD="${BCFTOOLS} view -i 'FORMAT/BD=\"FN\"' ${HAPPY_VCF} > ${FN_VCF}"
logInfo "Executing command: ${CMD}"
eval ${CMD}

logInfo "Script is done running"