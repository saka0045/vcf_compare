#!/usr/bin/python3

"""
Script to parse the accuracy result file to get the cDNA positions into a separate file
"""

__author__ = "Yuta Sakai"


import argparse
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", dest="input_file", required=True,
        help="Full path to the accuracy result file"
    )
    parser.add_argument(
        "-o", dest="output_directory", required=True,
        help="Full path to the directory to save files"
    )

    args = parser.parse_args()

    input_file = os.path.abspath(args.input_file)
    output_directory = os.path.normpath(args.output_directory)

    # Open accuracy result file and skip the header line
    accuracy_result_file = open(input_file, "r")
    accuracy_result_file.readline()

    accuracy_result_dict = {}

    # Parse the accuracy result file
    parse_accuracy_result_file(accuracy_result_dict, accuracy_result_file)

    # Make individual sample files with cDNA positions
    make_cdna_position_file(accuracy_result_dict, output_directory)

    accuracy_result_file.close()


def make_cdna_position_file(accuracy_result_dict, output_directory):
    """
    Make cDNA position file that contains cDNA variant positions per line for sample
    :param accuracy_result_dict:
    :param output_directory:
    :return:
    """
    for sample in accuracy_result_dict.keys():
        cdna_position_file = open(output_directory + "/" + sample + "_cdna_variants", "w")
        for cdna_coordinates in accuracy_result_dict[sample].keys():
            cdna_position_file.write(cdna_coordinates + "\n")
        cdna_position_file.close()


def parse_accuracy_result_file(accuracy_result_dict, accuracy_result_file):
    """
    Parses the accuracy result file and collects the cDNA variant position and the
    CLC variant frequency for a sample
    :param accuracy_result_dict:
    :param accuracy_result_file:
    :return:
    """
    for line in accuracy_result_file:
        line = line.rstrip()
        line_item = line.split("\t")
        sample_name = line_item[0]
        cdna_position = line_item[2].rstrip()
        if "," in cdna_position:
            cdna_position = cdna_position.split(",")[0]
        else:
            cdna_position = cdna_position.split(" ")[0]
        clc_vf = line_item[5].rstrip()
        if sample_name not in accuracy_result_dict.keys():
            accuracy_result_dict[sample_name] = {cdna_position: clc_vf}
        else:
            update_dict = {cdna_position: clc_vf}
            accuracy_result_dict[sample_name].update(update_dict)


if __name__ == "__main__":
    main()
