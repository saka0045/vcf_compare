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

    for line in input_file:
        line = line.rstrip()
        line_item = line.split(",")
        sample_name = line_item[0]
        # Skip the bioinformatics replicate samples
        if "rep" in sample_name:
            continue
        else:
            chromosome = line_item[1]
            position = line_item[2]
            ref = line_item[3]
            alt = line_item[4]
            depth = line_item[5]
            allele_frequency = line_item[7]

    input_file.close()


if __name__ == "__main__":
    main()
