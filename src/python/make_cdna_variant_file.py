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


if __name__ == "__main__":
    main()
