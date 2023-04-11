# Get the average time from npb raw data
# run with --help to get help information
# run with -d/--directory to set the raw data directory
# e.g. python get_average_time.py -d arm_init_A/

import os
import re
import argparse


def extract_time_from_log(file_path):
    times = []
    with open(file_path, "r") as file:
        for line in file:
            match = re.findall(r"Time in seconds =\s+(\d+\.\d+)", line)
            if match:
                times.append(float(match[0]))
    return times


def average(numbers):
    return sum(numbers) / len(numbers) if numbers else None


def extract_time(directory_path):
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        if os.path.isfile(file_path):
            times_in_file = extract_time_from_log(file_path)
            # if times_in_file is not None:
            #     print(f'File: {file_name}, Time in seconds: {times_in_file}')
            # else:
            #     print(f'File: {file_name} does not contain "Time in seconds" line')
            average_time = average(times_in_file)
            if average_time is not None:
                print(f"File: {file_name}, Time in seconds: {average_time}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Get the average time of the npb benchmark.",
    )
    parser.add_argument(
        "-d",
        "--directory",
        const=str,
        nargs="?",
        help="the directory contains log files",
    )
    args = parser.parse_args()

    if not args.directory:
        print("input directory is needed by '-d'")
        exit(1)

    extract_time(args.directory)
