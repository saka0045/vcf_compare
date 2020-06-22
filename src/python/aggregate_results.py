#!/usr/bin/python3

__author__ = "Yuta Sakai"


import argparse
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", dest="input_directory", required=True,
        help="Full path to the input directory with the *.summary.csv files"
    )

    args = parser.parse_args()

    input_directory = os.path.normpath(args.input_directory)
    file_list = os.listdir(input_directory)

    result_dict = {}
    for file in file_list:
        # Get the sample name from the file name
        sample_name = file.split(".")[0].split("_")[0]
        result_dict[sample_name] = {}
        # Open the summary.csv file
        summary_file = open(input_directory + "/" + file, "r")
        # Get the header info
        header_line = summary_file.readline().rstrip()
        header_list = header_line.split(",")
        for line in summary_file:
            line = line.rstrip()
            line_item = line.split(",")
            quality_filter = line_item[header_list.index("Filter")]
            # Only interested in ALL quality_filter
            if quality_filter == "PASS":
                continue
            else:
                # Parse out the summary depending on the variant_type
                variant_type = line_item[header_list.index("Type")]
                truth_total = line_item[header_list.index("TRUTH.TOTAL")]
                true_positive = line_item[header_list.index("TRUTH.TP")]
                false_negative = line_item[header_list.index("TRUTH.FN")]
                query_total = line_item[header_list.index("QUERY.TOTAL")]
                false_positive = line_item[header_list.index("QUERY.FP")]
                recall = line_item[header_list.index("METRIC.Recall")]
                precision = line_item[header_list.index("METRIC.Precision")]
                result_dict[sample_name][variant_type] = {
                    "truth_total": truth_total,
                    "query_total": query_total,
                    "true_positive": true_positive,
                    "false_positive": false_positive,
                    "false_negative": false_negative,
                    "precision": precision,
                    "recall": recall
                }
        summary_file.close()

    print(result_dict)


if __name__ == "__main__":
    main()
