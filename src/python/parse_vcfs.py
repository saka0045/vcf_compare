#!/usr/bin/python3

"""
Script to parse the false_positives.vcf and false_negatives.vcf to collect the depth
and the real allele frequency for each variant
"""

__author__ = "Yuta Sakai"


import argparse
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", dest="input_directory", required=True,
        help="Full path to the input directory with the vcf files"
    )
    parser.add_argument(
        "-o", dest="output_directory", required=True,
        help="Full path to the output directory to save result files"
    )

    args = parser.parse_args()

    input_directory = os.path.normpath(args.input_directory)
    file_list = os.listdir(input_directory)
    output_directory = os.path.normpath(args.output_directory)

    # Make result file and write out headers
    result_file = open(output_directory + "/parsed_vcf_results.csv", "w")
    result_file.write("Sample,CHROM,POS,REF,ALT,DP,Called AF,Real AF\n")

    # Parse the VCF files
    parse_vcf(file_list, input_directory, result_file)
    result_file.close()


def parse_vcf(file_list, input_directory, result_file):
    for file in file_list:
        vcf_file = open(input_directory + "/" + file, "r")
        for line in vcf_file:
            # Get header information
            if line.startswith("#CHROM"):
                line = line.rstrip()
                header_items = line.split("\t")
                sample_name = file.split(".")[0].split("_")[0]
            elif line.startswith("chr"):
                line = line.rstrip()
                line_item = line.split("\t")
                chrom = line_item[header_items.index("#CHROM")]
                position = line_item[header_items.index("POS")]
                ref = line_item[header_items.index("REF")]
                alt = line_item[header_items.index("ALT")].replace(",", ":")
                format_line = line_item[header_items.index("FORMAT")].split(":")
                sample_result = line_item[-1].split(":")
                try:
                    allele_depth = sample_result[format_line.index("AD")].split(",")
                    ref_depth = allele_depth[0]
                    alt_depth = allele_depth[1]
                    total_depth = int(ref_depth) + int(alt_depth)
                    real_allele_frequency = round(int(alt_depth) / total_depth, 4)
                except ValueError:
                    total_depth = "NA"
                    real_allele_frequency = "NA"
                # If AF exists, Replaces the "," in case there are multiple allele frequencies reported
                try:
                    called_allele_frequency = sample_result[format_line.index("AF")].replace(",", ":")
                except ValueError:
                    called_allele_frequency = "NA"
                line_to_write = [sample_name, chrom, position, ref, alt, str(total_depth), called_allele_frequency,
                                 str(real_allele_frequency)]
                result_file.write(",".join(line_to_write))
                result_file.write("\n")
        vcf_file.close()


if __name__ == "__main__":
    main()
