import os
import re
import sys


def digest_lstopo(file_path):
    """
    Utility script to extract information from `lstopo-no-graphics -p'.
    See: https://linux.die.net/man/1/lstopo
    :param file_path: Path to the .txt output of `lstopo-no-graphics -p' command
    :return: A list of tuples (pu_id, core_id, package_id) for all of the system's processing units (pus)
    """
    # Check if file exists
    if not os.path.isfile(file_path):
        print("Error file " + file_path + " doesn't exist")

    # Open file
    file_desc = open(file_path, "r")

    # Regular expressions
    package_pattern = re.compile("Package[ \t]+P#([0-9]+)")
    core_pattern = re.compile("Core[ \t]+P#([0-9]+)")
    pu_pattern = re.compile("PU[ \t]+P#([0-9]+)")

    cur_package = -1
    cur_core = -1

    # Scanning file
    result = {"packages": []}
    for line in file_desc:
        package_match = package_pattern.search(line)
        if package_match:
            cur_package = package_match.group(1)
            package_dict = {"id": cur_package, "cores": []}
            result["packages"].append(package_dict)
            continue

        core_match = core_pattern.search(line)
        if core_match:
            cur_core = core_match.group(1)
            core_dict = {"id": cur_core, "cpus": []}
            package_dict["cores"].append(core_dict)
            continue

        pu_match = pu_pattern.search(line)
        if pu_match:
            cur_pu = pu_match.group(1)
            if cur_package == -1 or cur_core == -1:
                print(
                    "Error cur_package "
                    + str(cur_package)
                    + " cur_core "
                    + str(cur_core)
                    + " on line "
                    + str(line)
                )
                continue
            core_dict["cpus"].append(cur_pu)

    return result


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: " + sys.argv[0] + " input file")
        sys.exit(1)

    # Iterate through each logical CPU's details
    for processing_unit, core, package in digest_lstopo(sys.argv[1]):
        print(processing_unit, core, package)
