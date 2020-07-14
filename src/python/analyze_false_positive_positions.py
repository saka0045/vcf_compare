#!/usr/bin/python3

"""
Script to look at the false positive variant positions and see how many occurrences there are
of that variant position. Requires the output file from parse_vcfs.py
"""

__author__ = "Yuta Sakai"


import argparse
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", dest="input_file", required=True,
        help="Full path to the result file produced by parse_vcfs.py"
    )
    parser.add_argument(
        "-o", dest="output_directory", required=True,
        help="Full path to the output directory to save result files"
    )

    args = parser.parse_args()

    input_file_path = os.path.abspath(args.input_file)
    output_directory = os.path.normpath(args.output_directory)

    # Open the input file and skip the header line
    input_file = open(input_file_path, "r")
    input_file.readline()

    # Parse the result into a dictionary
    result_dict, sample_name_list = parse_input_file(input_file)

    # Make result file
    result_file = make_result_file(output_directory, result_dict, sample_name_list)

    print("Number of samples in samples analyzed: " + str(len(sample_name_list)))

    input_file.close()
    result_file.close()


def make_result_file(output_directory, result_dict, sample_name_list):
    result_file = open(output_directory + "/variant_positions.csv", "w")
    # Write header
    result_file.write(",")
    result_file.write(",".join(sample_name_list) + ",")
    result_file.write("Total Count\n")
    # Iterate through the variant location in result_dict
    for variant_location in result_dict.keys():
        result_file.write(variant_location + ",")
        # Go through the entire sample_name_list per variant_location
        for sample_name in sample_name_list:
            # Write in the alt allele if the sample_name exists in result_dict[variant_location]
            if sample_name in result_dict[variant_location].keys():
                result_file.write(result_dict[variant_location][sample_name] + ",")
            # Otherwise keep it blank
            else:
                result_file.write(",")
        # Add the total number of samples found in the variant_location
        result_file.write(str(len(result_dict[variant_location].keys())))
        result_file.write("\n")
    return result_file


def parse_input_file(input_file):
    """
    Parses the file from parse_vcfs.py and create a dictionary of variant locations
    :param input_file:
    :return:
    """
    result_dict = {}
    sample_name_list = []
    for line in input_file:
        line = line.rstrip()
        line_item = line.split(",")
        sample_name = line_item[0]
        # Skip the bioinformatics replicate samples
        if "rep" in sample_name:
            continue
        else:
            if sample_name not in sample_name_list:
                sample_name_list.append(sample_name)
            chromosome = line_item[1]
            position = line_item[2]
            ref = line_item[3]
            alt = line_item[4]
            depth = line_item[5]
            allele_frequency = line_item[7]
            variant_location = chromosome + ":" + position
            if variant_location not in result_dict.keys():
                result_dict[variant_location] = {sample_name: alt}
            else:
                result_to_add = {sample_name: alt}
                result_dict[variant_location].update(result_to_add)
    return result_dict, sample_name_list


if __name__ == "__main__":
    main()
