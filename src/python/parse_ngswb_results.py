#!/usr/bin/python3

"""
Script to compare the clinical NGSWB results to VCF results
"""

__author__ = "Yuta Sakai"


import argparse
import os
import sys
import re


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

    # Create the result file
    result_file = open(output_directory + "/NGSWB_Compare_Results.csv", "w")

    # Parse the NGSWB input file and copy the results to the new result file and append results, if found
    ngswb_file = parse_ngswb_file_and_write_results(ngswb_file_path, result_file, vcf_result_dict)

    ngswb_file.close()
    result_file.close()


def parse_ngswb_file_and_write_results(ngswb_file_path, result_file, vcf_result_dict):
    """
    Parses the NGSWB result file and searches for same result in the vcf_result_dict and writes results
    to the result file
    :param ngswb_file_path: This NGSWB result file needs to be in CSV format
    :param result_file:
    :param vcf_result_dict:
    :return:
    """
    ngswb_file = open(ngswb_file_path, "r")
    header_line = ngswb_file.readline().rstrip()
    result_file.write(header_line)
    header_item = header_line.split(",")
    result_file.write(",Found in MGC,MGC Genomic,MGC Position Coverage,MGC Variant Coverage,MGC Variant Frequency\n")
    for line in ngswb_file:
        results_written = False
        line = line.rstrip()
        result_file.write(line)
        line_item = line.split(",")
        sample = line_item[header_item.index("Sample")]
        # Get the chromosome, position, ref and alt from the "Genomic" cell
        genomic_position = line_item[header_item.index("Genomic")]
        chromosome = genomic_position.split(":")[0]
        position_string = genomic_position.split(".")[1]
        position = ''.join(filter(str.isdigit, position_string))
        genomic_change = position_string.replace(position, "")
        ref = genomic_change.split(">")[0]
        alt = genomic_change.split(">")[1]
        # Each position needs to be searched for multi-allelic sites
        for position_key in vcf_result_dict[sample].keys():
            if re.search(position, position_key):
                # See if the chromosome, ref and alt matches
                if (chromosome == vcf_result_dict[sample][position_key]["chrom"] and
                        ref == vcf_result_dict[sample][position_key]["ref"] and
                        alt == vcf_result_dict[sample][position_key]["alt"]):
                    mgc_genomic_string = (vcf_result_dict[sample][position_key]["chrom"] + ":g." +
                                          position + vcf_result_dict[sample][position_key]["ref"] + ">" +
                                          vcf_result_dict[sample][position_key]["alt"])
                    result_file.write(",Y," + mgc_genomic_string + "," +
                                      vcf_result_dict[sample][position_key]["total_depth"] + "," +
                                      vcf_result_dict[sample][position_key]["alt_depth"] + "," +
                                      vcf_result_dict[sample][position_key]["allele_frequency"] + "," +
                                      position_key + "\n")
                    results_written = True
                else:
                    continue
            else:
                continue
        # If no results are found, go to the next line
        if results_written == False:
            result_file.write(",N\n")
    return ngswb_file


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
                        "total_depth": str(total_depth),
                        "allele_frequency": str(real_allele_frequency)
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
                        "total_depth": str(total_depth),
                        "allele_frequency": str(real_allele_frequency)
                    }
                    muti_allelic_site.append(position)
        vcf.close()
    return vcf_result_dict


if __name__ == "__main__":
    main()
