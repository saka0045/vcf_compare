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

Script to analyze the false positive from MGC against the BAM file

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
PYTHON_SCRIPT_DIR="${SCRIPT_ROOT}/src/python"
SAMPLEDIR=""
COMMON_FUNC=""
LOG_DIR=""
LOG_FILE=""
SAMPLE=""
CMD=""
FALSE_POSITIVE_VCF=""
PYTHON3=""
FALSE_POSITIVE_BED=""
SORTED_BED=""
SORTED_MERGED_BED=""
BEDTOOLS=""
SORT=""
SAMTOOLS=""
BCFTOOLS=""
REF_GENOME=""
MGC_BAM=""
FP_CHECK_VCF=""
REAL_POSITIVE_VCF=""

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
FALSE_POSITIVE_VCF="${SAMPLEDIR}/${SAMPLE}_MGC_false_positives.vcf"
validateFile "${FALSE_POSITIVE_VCF}"

# Source python 3.6.3
logInfo "Sourcing python 3.6.3"
CMD="source ${PYTHON3}"
logInfo "Executing command: ${CMD}"
eval ${CMD}

# Run make_bed_from_vcf.py
logInfo "Running make_bed_from_vcf.py to create BED file from false positive vcf"
CMD="python ${PYTHON_SCRIPT_DIR}/make_bed_from_vcf.py -i ${FALSE_POSITIVE_VCF} -o ${SAMPLEDIR}"
logInfo "Executing command: ${CMD}"
eval ${CMD}

# Sort and merge the output BED
FALSE_POSITIVE_BED="${SAMPLEDIR}/${SAMPLE}_false_positive.bed"
SORTED_BED="${SAMPLEDIR}/${SAMPLE}_false_positive_sorted.bed"
SORTED_MERGED_BED="${SAMPLEDIR}/${SAMPLE}_false_positive_sorted_merged.bed"
logInfo "Sorting false_positived.bed"
CMD="${SORT} -k1,1 -k2,2n ${FALSE_POSITIVE_BED} > ${SORTED_BED}"
logInfo "Executing command: ${CMD}"
eval ${CMD}
logInfo "Merge overlapping region in BED file"
CMD="${BEDTOOLS} merge -i ${SORTED_BED} > ${SORTED_MERGED_BED}"
logInfo "Executing command: ${CMD}"
eval ${CMD}
logInfo "Removing the original BED file and sorted BED file"
CMD="rm ${FALSE_POSITIVE_BED} ${SORTED_BED}"
logInfo "Executing command: ${CMD}"
eval ${CMD}

# Run samtools mpileup and bcftools call to get the VCF out of input BAM
# using the false positive BED file
logInfo "Running samtools mpileup and bcftools call"
MGC_BAM="${SAMPLEDIR}/mgc/alignment/${SAMPLE}.bam"
FP_CHECK_VCF="${SAMPLEDIR}/${SAMPLE}_fp_check.vcf"
CMD="${SAMTOOLS} mpileup -l ${SORTED_MERGED_BED} -f ${REF_GENOME} -g ${MGC_BAM} | \
${BCFTOOLS} call -c > ${FP_CHECK_VCF}"
logInfo "Executing command: ${CMD}"
eval ${CMD}

# Filter the "0/0" calls from _fp_check.vcf to keep the true variants found in BAM
REAL_POSITIVE_VCF="${SAMPLEDIR}/${SAMPLE}_true_positive.vcf"
logInfo "Filtering 0/0 calls from fp_check.vcf"
CMD="${BCFTOOLS} view -e 'FORMAT/GT=\"0/0\"' ${FP_CHECK_VCF} > ${REAL_POSITIVE_VCF}"
logInfo "Executing command: ${CMD}"
eval ${CMD}

logInfo "Script is done running"