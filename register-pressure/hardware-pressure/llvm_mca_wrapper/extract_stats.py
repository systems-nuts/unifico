import os
import argparse
import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from jsonstream import load

EXAMPLE_JSON = "json/fact_aarch64.json"
REGISTER_FILE_RE = r"Max number of mappings used:\s*(\d+)"


def bar_plot(
    labels,
    y1,
    y2,
    y1_label="y1_label",
    y2_label="y2_label",
    ylabel="",
    title="",
    save_fig="",
):
    """
    A simple wrapper for matplotlib's barplot.

    :param labels:
    :param y1:
    :param y2:
    :param ylabel:
    :param xlabel:
    :param save_fig:
    :return:
    """
    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    ax.bar(x - width / 2, y1, width, label=y1_label)
    ax.bar(x + width / 2, y2, width, label=y2_label)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    fig.tight_layout()

    plt.show()
    if len(save_fig) > 0:
        plt.savefig(save_fig)


def parse_mca_json(file_path):
    """Decode the json file produced by llvm-mca tool

    llvm-mca with the `--json` option returns a file with a list of JSON objects one after the other.
    So, we parse them with the `jsonstream` library:
    https://pypi.org/project/jsonstream/
    and we return a dictionary with keys:

    * InstructionInfo
    * Summary
    * Timeline
    * ResourcePressure

    Works with LLVM 13.
    Currently, the info contained in the JSON file is described briefly here:
    https://reviews.llvm.org/D86644?id=318077
    @param file_path
    @return: list of json objects
    """
    with open(file_path, "r") as fp:
        stats_list = list(load(fp))

    mca_dict = {
        "InstructionInfo": stats_list[0],
        "Summary": stats_list[1],
        "Timeline": stats_list[2],
        "ResourcePressure": stats_list[3],
    }
    return mca_dict


def parse_mca_text(file_path):
    """Decode the text file produced by llvm-mca tool

    llvm-mca returns a file with a list of statistics.
    For now we parse only the register file stats. TODO

    Works with LLVM 13.
    @param file_path
    @return: list of json objects
    """
    with open(file_path, "r") as fp:
        lines = fp.readlines()
        for line in lines:
            matchResult = re.match(REGISTER_FILE_RE, line)
            if matchResult:
                return int(matchResult.group(1))


def resource_pressure(mca_dict):
    """Get a dictionary with the total pressure for every hardware resource in the mca_dict

    Suppose that the mca_dict contains `n` instructions.
    Their indices are numbered from 0 to `n - 1`.
    Currently, the element indexed `n` inside the list given by the `ResourcePressureInfo` key,
    is the resource pressure per iteration, for the specific hardware resource.
    So, we just return these elements of the list for every resource index.
    @param mca_dict: a dictionary as returned by the function `parse_mca_json`
    @return: dictionary with total pressures
    """
    n = len(mca_dict["Timeline"])
    resources = mca_dict["InstructionInfo"]["Resources"][
        "Resources"
    ]  # Resources names

    return {
        resources[instr_dict["ResourceIndex"]]: instr_dict["ResourceUsage"]
        for instr_dict in mca_dict["ResourcePressure"]["ResourcePressureInfo"]
        if instr_dict["InstructionIndex"] == n
    }


def sort_by_pressure(folder_path, target_resources):
    """Sort the assembly files in a folder based on hardware pressure

    Calculates the hardware pressure for the given resources, for all the resources of the JSON files in a folder.
    Hardware pressure per file is summed for all the resources.
    JSON files are created through the `llvm-mca --json` command and must be of the same architecture.
    @param folder_path: the location of the json files
    @param target_resources: list of processor resources
    @return: list with program names with their pressures in ascending order
    """
    result = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if not os.path.isfile(file_path):
            continue
        mca_dict = parse_mca_json(file_path)
        pressure_dict = resource_pressure(mca_dict)
        total_pressure = sum(
            [
                pressure_dict[resource]
                for resource in pressure_dict.keys()
                if resource in target_resources
            ]
        )
        result.append([file, total_pressure])

    result = sorted(
        result, key=lambda x: x[1]
    )  # Sort list of tuples based on the 2nd argument, i.e. total_pressure

    return list(zip(*result))


def folder_pressure(folder_path, target_resources):
    """Sum the hardware pressure of all assembly files in a folder

    Sums the hardware pressure for the given target resources, for all the resources of the JSON files in a folder.
    Hardware pressure per file is summed for all the resources.
    JSON files are created through the `llvm-mca --json` command and must be of the same architecture.
    @param folder_path: the location of the json files
    @param target_resources: list of processor resources
    @return: tuple with the folder name and the sum of pressures for all files
    """
    pressures = sort_by_pressure(folder_path, target_resources)[
        1
    ]  # Get only the numbers, not the file names.
    folder_name = folder_path.split("/")[-1]
    return folder_name, sum(pressures)


def folder_register_pressure(folder_path):
    """Find the max of register pressure of all text files in a folder

    Find the max of register pressure for all the resources of the text files in a folder.
    Text files are created through the `llvm-mca` command and must be of the same architecture.
    @param folder_path: the location of the text files
    @return: tuple with the folder name and the max of pressures for all files
    """
    register_pressures = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if not os.path.isfile(file_path):
            continue
        # if not folder_path.split('/')[-1] in file:
        #     continue
        register_pressure = parse_mca_text(file_path)
        register_pressures.append(register_pressure)

    folder_name = folder_path.split("/")[-1]
    return folder_name, sum(register_pressures)


def multi_folder_pressure(folder_path, target_resources):
    """Get the hardware pressure of all folders in a folder

    Calculate the hardware pressure for the given target resources, for all the folders with JSON files in a folder.
    Hardware pressure per folders is summed for all the resources.
    JSON files are created through the `llvm-mca --json` command and must be of the same architecture.
    @param folder_path: the location of the folders with the json files
    @param target_resources: list of processor resources
    @return: list with folder names with their total pressures
    """
    result = []
    for folder in os.listdir(folder_path):
        inner_folder_path = os.path.join(folder_path, folder)
        if not os.path.isdir(inner_folder_path):
            continue
        result.append(folder_pressure(inner_folder_path, target_resources))

    names = list(zip(*result))[0]
    pressures = list(zip(*result))[1]
    return pd.DataFrame(index=names, data=pressures, columns=["HW Pressure"])


def multi_folder_register_pressure(folder_path):
    """Get the register pressure of all folders in a folder

    Calculate the register pressure for all the folders with text files in a folder.
    Text files are created through the `llvm-mca` command and must be of the same architecture.
    @param folder_path: the location of the folders with the json files
    @return: list with folder names with their register pressures
    """
    result = []
    for folder in os.listdir(folder_path):
        inner_folder_path = os.path.join(folder_path, folder)
        if not os.path.isdir(inner_folder_path):
            continue
        result.append(folder_register_pressure(inner_folder_path))

    names = list(zip(*result))[0]
    pressures = list(zip(*result))[1]
    return pd.DataFrame(
        index=names, data=pressures, columns=["Register Pressure"]
    )


def plot_by_pressure(folder_path, target_resources):
    """Plot the assembly files in a folder based on hardware pressure

    Calculates the hardware pressure for the given resources, for all the resources of the JSON files in a folder.
    Plots the hardware pressure for every in ascending order.
    Hardware pressure per file is summed for all the resources.
    JSON files are created through the `llvm-mca --json` command and must be of the same architecture.
    @param folder_path: the location of the json files
    @param target_resources: list of processor resources
    @return:
    """
    pressure_list = sort_by_pressure(folder_path, target_resources)
    plt.bar(pressure_list[0], pressure_list[1])
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Utility script for extracting hardware pressure, "
        "as JSON, from assembly files."
    )
    parser.add_argument(
        "--asm-folder",
        action="store",
        required=True,
        help="folder containing the assembly files",
    )

    args, others = parser.parse_known_args()

    df_overhead = pd.read_csv("json/sole/overheads.csv", index_col="Benchmark")

    FLAGS = "O0 O1 O2 O3"
    for flag in FLAGS.split(" "):
        print("Flag: ", flag)

        directory = os.path.join(
            "json/sole/mca-results/hw-pressure-" + flag, "aarch64"
        )
        df_hw_pressure = multi_folder_pressure(
            directory,
            [
                "THX2T99P0",
                "THX2T99P1",
                "THX2T99P2",
                "THX2T99P3",
                "THX2T99P4",
                "THX2T99P5",
            ],
        )

        directory = os.path.join(
            "json/sole/mca-results/reg-pressure-" + flag, "aarch64"
        )
        df_reg_pressure = multi_folder_register_pressure(directory)

        df = df_hw_pressure.join(df_reg_pressure)
        df = df.join(df_overhead)
        df.dropna(inplace=True)
        df.sort_values(by=["Overhead -" + flag], inplace=True)
        # df.sort_values(by=['Register Pressure'], inplace=True)
        # df.plot.bar(['HW Pressure', 'Register Pressure', 'Overhead -' + flag])
        ax = df[
            ["Overhead -" + flag, "HW Pressure", "Register Pressure"]
        ].plot.bar(subplots=True)
        ax[1].legend(loc=2)
        plt.savefig("json/sole/pressure-" + flag + ".png")
        plt.show()
        # bar_plot(benchmarks_sorted, hw_pressures_sorted, reg_pressures_sorted,
        #          y1_label='hardware-pressure', y2_label='register_file_pressure')
