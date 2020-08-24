#!/usr/bin/python3

"""
Script to compare the clinical NGSWB results to VCF results
"""

__author__ = "Yuta Sakai"


import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", dest="input_directory", required=True,
        help="Full path to the input directory with the VCFs"
    )
    parser.add_argument(
        "-f", dest="ngswb_file", required=True,
        help="Full path to the NGSWB result file in CSV format"
    )
    parser.add_argument(
        "-o", dest="output_directory", required=True,
        help="Full path to the directory to save the result file"
    )

    args = parser.parse_args()

    input_directory = os.path.normpath(args.input_directory)
    ngswb_file_path = os.path.abspath(args.ngswb_file)
    output_directory = os.path.normpath(args.output_directory)

    # Parse the VCFs to gather all variant information
    vcf_result_dict = parse_vcf_to_dict(input_directory)


def parse_vcf_to_dict(input_directory):
    """
    Parses VCF results into python dictionary
    For each sample, it uses the variant position as the key, for multi-allelic variant, it will append
    a number for each multi-allelic variant: {position}-{number}
    :param input_directory:
    :return:
    """
    vcf_result_dict = {}
    vcf_list = os.listdir(input_directory)
    for file in vcf_list:
        vcf = open(input_directory + "/" + file, "r")
        for line in vcf:
            if line.startswith("#CHROM"):
                line = line.rstrip()
                header_items = line.split("\t")
                sample_name = file.split(".")[0].split("_")[0]
                muti_allelic_site = []
                if sample_name not in vcf_result_dict.keys():
                    print("Processing sample: " + sample_name)
                    vcf_result_dict[sample_name] = {}
                else:
                    print("Duplicate sample found in VCF list, exiting script")
                    sys.exit()
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
                    alt_depth = "NA"
                    total_depth = "NA"
                    real_allele_frequency = "NA"
                if position not in vcf_result_dict[sample_name].keys():
                    vcf_result_dict[sample_name][position] = {
                        "chrom": chrom,
                        "ref": ref,
                        "alt": alt,
                        "alt_depth": alt_depth,
                        "total_depth": total_depth,
                        "allele_frequency": real_allele_frequency
                    }
                    muti_allelic_site.append(position)
                else:
                    # If a multi-allelic variant, append a number after the position
                    print("Duplicate variant position found for: ")
                    print(sample_name + ": " + chrom + " " + position)
                    new_position = position + "-" + str(muti_allelic_site.count(position) + 1)
                    vcf_result_dict[sample_name][new_position] = {
                        "chrom": chrom,
                        "ref": ref,
                        "alt": alt,
                        "alt_depth": alt_depth,
                        "total_depth": total_depth,
                        "allele_frequency": real_allele_frequency
                    }
                    muti_allelic_site.append(position)
        vcf.close()
    return vcf_result_dict


if __name__ == "__main__":
    main()
