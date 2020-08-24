#!/usr/bin/python3

"""
Script to parse the accuracy result between CLC and MGC
"""

__author__ = "Yuta Sakai"


import argparse
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", dest="input_directory", required=True,
        help="Full path to the input directory with _mgc_reported_variants.vcf files"
    )
    parser.add_argument(
        "-f", dest="accuracy_file_path", required=True,
        help="Full path to the initial accuracy result file used for make_cdna_variant_file.py"
    )
    parser.add_argument(
        "-o", dest="output_directory", required=True,
        help="Full path to directory to save the result file"
    )

    args = parser.parse_args()

    input_directory = os.path.normpath(args.input_directory)
    accuracy_file_path = os.path.abspath(args.accuracy_file_path)
    output_directory = os.path.normpath(args.output_directory)

    # Open accuracy file and skip the header
    accuracy_file = open(accuracy_file_path, "r")
    accuracy_file.readline()

    accuracy_result_dict = {}

    # Parse the accuracy file to gather CLC reported variant info
    parse_accuracy_file(accuracy_file, accuracy_result_dict)
    accuracy_file.close()

    # Parse the MGC VCFs to gather MGC reported variant info
    parse_mgc_vcf(accuracy_result_dict, input_directory)

    # Write the result out to a file
    make_result_file(accuracy_result_dict, output_directory)


def make_result_file(accuracy_result_dict, output_directory):
    """
    Create the result file
    :param accuracy_result_dict:
    :param output_directory:
    :return:
    """
    result_file = open(output_directory + "/parsed_accuracy_results.txt", "w")
    result_file.write("Sample\tGene (CLC)\tCLC Result\tCLC Position Coverage\tCLC Variant Coverage\tCLC VF\t"
                      "Gene (MGC)\tcDNA Variant (MGC)\tMGC Position Coverage\tMGC Variant Coverage\tMGC VF\n")
    for sample in accuracy_result_dict.keys():
        for clc_cdna_variant, result in accuracy_result_dict[sample].items():
            result_file.write(sample + "\t")
            write_result(result, "clc_gene", result_file)
            write_result(result, "clc_cdna_variant_line", result_file)
            write_result(result, "clc_position_coverage", result_file)
            write_result(result, "clc_variant_coverage", result_file)
            write_result(result, "clc_vf", result_file)
            write_result(result, "mgc_gene", result_file)
            write_result(result, "mgc_cdna_variant", result_file)
            write_result(result, "mgc_position_coverage", result_file)
            write_result(result, "mgc_variant_coverage", result_file)
            write_result(result, "mgc_vf", result_file)
            result_file.write("\n")
    result_file.close()


def write_result(dict, key_string, file):
    """
    Write out the result to the file if the key exists in accuracy_result_dict
    :param dict:
    :param key_string:
    :param file:
    :return:
    """
    try:
        file.write(dict[key_string] + "\t")
    except KeyError:
        file.write("NA\t")


def parse_mgc_vcf(accuracy_result_dict, input_directory):
    """
    Parses the MGC VCF and adds the result to accuracy_result_dict
    :param accuracy_result_dict:
    :param input_directory:
    :return:
    """
    mgc_vcf_list = os.listdir(input_directory)
    for file in mgc_vcf_list:
        mgc_vcf_file = open(input_directory + "/" + file, "r")
        sample_name = file.split("_")[0]
        for line in mgc_vcf_file:
            line = line.rstrip()
            line_item = line.split("\t")
            chromosome = line_item[0]
            position = line_item[1]
            ref = line_item[3]
            alt = line_item[4]
            info_item = line_item[7].split(";")
            # Get the gene from info line under "CAVA_GENE="
            mgc_gene = [i for i in info_item if "CAVA_GENE" in i][0].split("=")[1]
            # Get the cDNA variant position from info line under "CAVA_CSN="
            # CAVA_CSN has both the cDNA variant and protein variant separated by "_p."
            mgc_cdna_variant = [i for i in info_item if "CAVA_CSN" in i][0].split("=")[1].split("_p.")[0]
            # Gather position coverage, variant coverage and variant frequency
            format_header = line_item[8].split(":")
            sample_result = line_item[9].split(":")
            allele_depth = sample_result[format_header.index("AD")].split(",")
            mgc_position_coverage = int(allele_depth[0]) + int(allele_depth[1])
            mgc_variant_coverage = int(allele_depth[1])
            mgc_vf = round(mgc_variant_coverage / mgc_position_coverage, 4)
            for key in accuracy_result_dict[sample_name].keys():
                if key in mgc_cdna_variant:
                    update_dict = {
                        "mgc_gene": mgc_gene,
                        "mgc_cdna_variant": mgc_cdna_variant,
                        "mgc_position_coverage": str(mgc_position_coverage),
                        "mgc_variant_coverage": str(mgc_variant_coverage),
                        "mgc_vf": str(mgc_vf)
                    }
                    accuracy_result_dict[sample_name][key].update(update_dict)
        mgc_vcf_file.close()


def parse_accuracy_file(accuracy_file, accuracy_result_dict):
    """
    Parses the accuracy result file and gather CLC reported variant info
    :param accuracy_file:
    :param accuracy_result_dict:
    :return:
    """
    for line in accuracy_file:
        line = line.rstrip()
        line_item = line.split("\t")
        sample_name = line_item[0].rstrip()
        clc_gene = line_item[1].rstrip()
        clc_cdna_variant_line = line_item[2].rstrip()
        if "," in clc_cdna_variant_line:
            clc_cdna_variant = clc_cdna_variant_line.split(",")[0]
        else:
            clc_cdna_variant = clc_cdna_variant_line.split(" ")[0]
        clc_position_coverage = line_item[3].rstrip()
        clc_variant_coverage = line_item[4].rstrip()
        clc_vf = line_item[5].rstrip()
        if sample_name not in accuracy_result_dict.keys():
            accuracy_result_dict[sample_name] = {}
            accuracy_result_dict[sample_name][clc_cdna_variant] = {
                "clc_gene": clc_gene,
                "clc_cdna_variant_line": clc_cdna_variant_line,
                "clc_position_coverage": clc_position_coverage,
                "clc_variant_coverage": clc_variant_coverage,
                "clc_vf": clc_vf
            }
        else:
            accuracy_result_dict[sample_name][clc_cdna_variant] = {
                "clc_gene": clc_gene,
                "clc_cdna_variant_line": clc_cdna_variant_line,
                "clc_position_coverage": clc_position_coverage,
                "clc_variant_coverage": clc_variant_coverage,
                "clc_vf": clc_vf
            }


if __name__ == "__main__":
    main()
