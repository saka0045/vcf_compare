#!/usr/bin/python3

"""
Script to convert vcf file into BED file to use for samtools mpileup
"""

__author__ = "Yuta Sakai"


import argparse
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", dest="input_vcf", required=True,
        help="Full path to the vcf file"
    )
    parser.add_argument(
        "-o", dest="output_directory", required=True,
        help="Full path to the output directory to save the converted bed file"
    )

    args = parser.parse_args()

    input_file_path = os.path.abspath(args.input_vcf)
    output_directory = os.path.normpath(args.output_directory)

    # Get the sample name from the file name
    sample_name = os.path.basename(input_file_path).split("_")[0]
    print(sample_name)

    vcf_file = open(input_file_path, "r")
    bed_file = open(output_directory + "/" + sample_name + "_false_positive.bed", "w")

    # Parse the vcf file and make it into a bed file
    for line in vcf_file:
        # Get header information
        if line.startswith("#CHROM"):
            line = line.rstrip()
            header_items = line.split("\t")
        elif line.startswith("chr"):
            line = line.rstrip()
            line_item = line.split("\t")
            chrom = line_item[header_items.index("#CHROM")]
            position = line_item[header_items.index("POS")]
            ref = line_item[header_items.index("REF")]
            alt = line_item[header_items.index("ALT")]
            # Make the bed start position 0 based
            bed_start_position = int(position) - 1
            # The end region should be the length of REF or ALT, whichever one is longer
            # If they are the same length, take the REF length
            if len(ref) >= len(alt):
                bed_stop_position = bed_start_position + len(ref)
            else:
                bed_stop_position = bed_start_position + len(alt)
            # write out the result to the bed file
            result_to_write = [chrom, str(bed_start_position), str(bed_stop_position)]
            bed_file.write("\t".join(result_to_write) + "\n")

    vcf_file.close()
    bed_file.close()


if __name__ == "__main__":
    main()
