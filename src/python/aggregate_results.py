#!/usr/bin/python3

"""
Script to parse out the .summary.csv file from hap.py and aggregate the results to
separate result files based on the variant type
"""

__author__ = "Yuta Sakai"


import argparse
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", dest="input_directory", required=True,
        help="Full path to the input directory with the *.summary.csv files"
    )
    parser.add_argument(
        "-o", dest="output_directory", required=True,
        help="Full path to the output directory to save result files"
    )

    args = parser.parse_args()

    input_directory = os.path.normpath(args.input_directory)
    file_list = os.listdir(input_directory)
    output_directory = os.path.normpath(args.output_directory)

    # Parse all of the .summary.csv files
    result_dict = {}
    parse_summary_file(file_list, input_directory, result_dict)

    # Make the result file per variant type
    write_result_file(output_directory, result_dict, "INDEL")
    write_result_file(output_directory, result_dict, "SNP")
    write_result_file(output_directory, result_dict, "ALL")


def write_result_file(output_directory, result_dict, variant_type):
    """
    Writes the csv result file based on the variant_type
    :param output_directory:
    :param result_dict:
    :param variant_type: variant_type string in result_dict; "INDEL", "SNP" or "ALL"
    :return:
    """
    result_file = open(output_directory + "/" + variant_type + ".csv", "w")
    result_file.write("Sample,Truth,Query,TP,FP,FN,Precision,Recall\n")
    for sample in result_dict.keys():
        truth_total = str(result_dict[sample][variant_type]["truth_total"])
        query_total = str(result_dict[sample][variant_type]["query_total"])
        true_positive = str(result_dict[sample][variant_type]["true_positive"])
        false_positive = str(result_dict[sample][variant_type]["false_positive"])
        false_negative = str(result_dict[sample][variant_type]["false_negative"])
        precision = str(result_dict[sample][variant_type]["precision"])
        recall = str(result_dict[sample][variant_type]["recall"])
        item_to_write = [sample, truth_total, query_total, true_positive, false_positive, false_negative,
                         precision, recall]
        result_file.write(",".join(item_to_write))
        result_file.write("\n")
    result_file.close()


def parse_summary_file(file_list, input_directory, result_dict):
    """
    Function to parse the individual summary.csv file
    :param file_list:
    :param input_directory:
    :param result_dict:
    :return:
    """
    for file in file_list:
        # Get the sample name from the file name
        sample_name = file.split(".")[0].split("_")[0]
        result_dict[sample_name] = {}
        # Open the summary.csv file
        summary_file = open(input_directory + "/" + file, "r")
        # Get the header info
        header_line = summary_file.readline().rstrip()
        header_list = header_line.split(",")
        all_truth_total = 0
        all_query_total = 0
        all_true_positive = 0
        all_false_negative = 0
        all_false_positive = 0
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
                truth_total = int(line_item[header_list.index("TRUTH.TOTAL")])
                true_positive = int(line_item[header_list.index("TRUTH.TP")])
                false_negative = int(line_item[header_list.index("TRUTH.FN")])
                query_total = int(line_item[header_list.index("QUERY.TOTAL")])
                false_positive = int(line_item[header_list.index("QUERY.FP")])
                recall = float(line_item[header_list.index("METRIC.Recall")])
                precision = float(line_item[header_list.index("METRIC.Precision")])
                result_dict[sample_name][variant_type] = {
                    "truth_total": truth_total,
                    "query_total": query_total,
                    "true_positive": true_positive,
                    "false_positive": false_positive,
                    "false_negative": false_negative,
                    "precision": precision,
                    "recall": recall
                }
                # Sum the numbers from INDEL and SNP
                all_truth_total += truth_total
                all_query_total += query_total
                all_true_positive += true_positive
                all_false_negative += false_negative
                all_false_positive += false_positive
        # Calculate the overall precision and recall
        all_precision = round((all_true_positive / (all_true_positive + all_false_positive)), 7)
        all_recall = round((all_true_positive / (all_true_positive + all_false_negative)), 7)
        result_dict[sample_name]["ALL"] = {
            "truth_total": all_truth_total,
            "query_total": all_query_total,
            "true_positive": all_true_positive,
            "false_positive": all_false_positive,
            "false_negative": all_false_negative,
            "precision": all_precision,
            "recall": all_recall
        }
        summary_file.close()


if __name__ == "__main__":
    main()
