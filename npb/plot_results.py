import pandas as pd
import os
import re
import json

import matplotlib.pyplot as plt

import seaborn as sns

# This verbose and more readable regex form, requires the re.VERBOSE flag in re.compile
RESULT_FILE_REGEX = re.compile(
    r"""
 (\w+)      # Benchmark 
 \.         # Delimiter
 (\w+)      # Architecture 
 \.         # Delimiter
 (\w+)      # NPB Class
 \.         # Delimiter
 (\d+)      # Iteration
 \.out      # Suffix
""",
    re.VERBOSE,
)


def get_info(json_path):
    """
    Extract experiment info from json file
    @param json_path:
    @return:
    """
    with open(json_path, "r") as fp:
        d = json.load(fp)
    return d


def verify_npb_output(out_path):
    """
    Verify that npb output file includes a successful run
    @param out_path: npb output file path
    :return: boolean
    """
    with open(out_path, "r") as fp:
        for line in fp:
            if re.search(r"Verification\s+=\s+SUCCESSFUL", line):
                return True
        return False


def df_from_dir(results_dir):
    """
    Extract DataFrame from multiple NPB results in a directory.
    @param results_dir: Directory containing multiple output files from NPB runs
    @return:
    """
    info_dict_path = "{}/info.json".format(results_dir)
    if not os.path.isfile(info_dict_path):
        print("info.json not found")
        experiment = results_dir.split("/")[-1]
        flag = ""
    else:
        with open(info_dict_path, "r") as fp:
            info_dict = json.load(fp)
        experiment = info_dict["experiment"]["name"]
        # flag = info_dict['compiler']['flags']
        flag = "-O1"

    rows = []

    for output in os.listdir(results_dir):
        match = RESULT_FILE_REGEX.search(output)
        if match is None:
            continue
        bench = match.group(1)
        arch = match.group(2)
        bench_class = match.group(3)
        iteration = match.group(4)

        output_abs_path = os.path.join(results_dir, output)

        with open(output_abs_path, "r") as fp:
            verified = False
            verification_pattern = re.compile(r"Verification\s+=\s+SUCCESSFUL")
            time_pattern = re.compile(r"Time in seconds\s+=\s+(\d+\.\d+)")
            for line in fp:
                if verification_pattern.search(line):
                    verified = True
                match = time_pattern.search(line)
                if match is not None:
                    time = match.group(1)
            if not verified:
                print("Not verified: ", output)
                time = float("nan")

        out_dict = {
            "Experiment": experiment,  # TODO: redefine the notion of experiment
            "Flag": flag,
            "Benchmark": bench,
            "Architecture": arch,
            "Class": bench_class,
            "Iteration": int(iteration),
            "Time": float(time),
        }

        rows.append(out_dict)

    df = pd.DataFrame(rows)

    return df


# TODO: tests
def dataframe_to_catplot(df):
    """
    @param df: Pandas DataFrame
    """
    for bench in set(df["Benchmark"]):
        sns.catplot(
            x="Threads",
            y="Time",
            hue="Experiment",
            col="Affinity",
            data=df[(df["Benchmark"] == bench)],
            kind="box",
            palette="Set3",
        )
        plt.title(bench)
        plt.ylabel("Time (s)")
        plt.show()


def dataframe_to_boxplot(df, arch, hue="Experiment"):
    """
    @param df: Pandas DataFrame
    @param hue: Comparison variable for boxplot
    """
    # for bench in set(df['Benchmark']):
    df["positive"] = df["% Overhead"] > 0
    ax = df.plot.bar(
        x="Benchmark",
        y="% Overhead",
        color=df.positive.map({True: "r", False: "g"}),
    )
    # data=df,
    # palette='Set1')
    # plt.title(bench)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    plt.ylabel("% Overhead")
    plt.title(
        '{} overhead from "{}"- NPB class B'.format(arch, df["Experiment"][0])
    )
    plt.show()


def two_dataframes_boxplot(df1, df2):
    """
    @param df1: Pandas Dataframe
    @param df2: Pandas Dataframe
    """
    df = df1.append(df2, ignore_index=True)

    df1 = df[df["Affinity"] == "scatter"]
    df2 = df[df["Affinity"] == "compact"]
    for bench in set(df["Benchmark"]):
        plt.subplot(1, 2, 1)
        sns.boxplot(
            x="Threads",
            y="Time",
            hue="Experiment",
            data=df1[(df1["Benchmark"] == bench)],
            palette="Set3",
        )
        plt.legend(loc=1, prop={"size": 8})
        plt.title(bench)
        plt.subplot(1, 2, 2)
        sns.boxplot(
            x="Threads",
            y="Time",
            hue="Experiment",
            data=df2[(df2["Benchmark"] == bench)],
            palette="Set3",
        )
        plt.legend(loc=1, prop={"size": 8})
        plt.title(bench)
        plt.savefig(bench)
        plt.show()


def get_overhead_df(dir1, dir2, arch, npb_class="B", out_file=None):
    """
    Get the overhead dataframe between two different experiments.

    @param dir1: Output files for first experiment
    @param dir2: Output files for second experiment
    @param arch: Architecture to focus on
    @param npb_class: Which NPB class to examine
    @param out_file: Optional path to csv output
    @return:
    """
    if not os.path.isdir(dir1):
        print("{} result directory does not exist.".format(dir1))
    elif not os.path.isdir(dir2):
        print("{} result directory does not exist.".format(dir2))

    df1 = df_from_dir(dir1)
    df1 = df1[df1["Architecture"] == arch]
    df1 = df1[df1["Class"] == npb_class]

    df2 = df_from_dir(dir2)
    df2 = df2[df2["Architecture"] == arch]
    df2 = df2[df2["Class"] == npb_class]

    exp1 = df1.iloc[0, 0]
    exp2 = df2.iloc[0, 0]

    # flag = info1['compiler']['flags'] TODO: always include info.json
    flag = df2.iloc[0, 1]

    df1 = df1.groupby(["Benchmark"]).mean()
    df2 = df2.groupby(["Benchmark"]).mean()

    title = '"{}" vs "{}" {}'.format(exp2, exp1, flag)

    total_df = df1.append(df2, ignore_index=True)
    # total_df.sort_values(by=['Benchmark', 'Class', 'Threads', 'Iteration'], inplace=True)
    df1.sort_values(by=["Benchmark", "Iteration"], inplace=True)
    df2.sort_values(by=["Benchmark", "Iteration"], inplace=True)
    df = pd.DataFrame(df1)
    df["% Overhead"] = df["Time"].combine(
        df2["Time"], lambda x1, x2: (x2 / x1 - 1) * 100
    )
    df.drop(["Iteration", "Time"], axis=1, inplace=True)
    df["Benchmark"] = df.index
    df["Experiment"] = exp2
    df.reset_index(drop=True, inplace=True)

    if out_file:
        df.to_csv(out_file, index=False)
    return df


def compare_single_thread_exp(dir1, dir2, out_plot):
    """
    Plot the graphs of the two experiments in each directory
    @param dir1: Output files for first experiment
    @param dir2: Output files for first experiment
    @param out_plot: Output dir
    @return:
    """
    if not os.path.isdir(dir1):
        print("{} result directory does not exist.".format(dir1))
    elif not os.path.isdir(dir2):
        print("{} result directory does not exist.".format(dir2))

    df1 = df_from_dir(dir1)
    df1 = df1[df1["Class"] == "A"]
    df2 = df_from_dir(dir2)
    df2 = df2[df2["Class"] == "A"]

    info1 = get_info(os.path.join(dir1, "info.json"))
    info2 = get_info(os.path.join(dir2, "info.json"))

    exp1 = info1["experiment"]["name"]
    exp2 = info2["experiment"]["name"]
    exp2 = "remove 15 registers"
    df2["Experiment"] = exp2
    flag = info1["flag"]

    total_df = df1.append(df2, ignore_index=True)
    # total_df.sort_values(by=['Benchmark', 'Class', 'Threads', 'Iteration'], inplace=True)
    df1.sort_values(by=["Benchmark", "Class", "Iteration"], inplace=True)
    df1 = df1.reset_index(drop=True)
    df2.sort_values(by=["Benchmark", "Class", "Iteration"], inplace=True)
    df2 = df2.reset_index(drop=True)
    df = pd.DataFrame(df1)
    df["% Overhead"] = df["Time"].combine(
        df2["Time"], lambda x1, x2: (x2 / x1 - 1) * 100
    )
    for bench in set(df["Benchmark"]):
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        sns.set_context(
            rc={"font.size": 14, "axes.titlesize": 24, "axes.labelsize": 16}
        )
        # sns.boxplot(x='Threads', y='Time', hue='Experiment',
        #             data=total_df[(total_df['Benchmark'] == bench)],
        #             palette='Set3')
        sns.stripplot(
            x="Threads",
            y="Time",
            hue="Experiment",
            data=total_df[(total_df["Benchmark"] == bench)],
            size=6,
            color=".3",
            linewidth=0,
            palette="Set1",
        )
        plt.legend(loc=1, prop={"size": 8})
        plt.ylabel("Time (s)")
        plt.legend(fontsize="medium", title_fontsize="20")
        plt.subplot(1, 2, 2)
        sns.set_context(
            rc={"font.size": 14, "axes.titlesize": 24, "axes.labelsize": 16}
        )
        sns.boxplot(
            x="Threads",
            y="% Overhead",
            hue="Class",
            data=df[(df["Benchmark"] == bench)],
            palette="Set3",
        )
        plt.legend([], [], frameon=False)
        bench_out_plot = "{}_{}".format(out_plot, bench)
        title = '{} - "{}" vs "{}" {}'.format(bench, exp2, exp1, flag)
        plt.suptitle(title)
        plt.savefig(bench_out_plot, bbox_inches="tight")
        plt.show()


def compare_experiments(dir1, dir2, out_plot, hue="Experiment", how="side"):
    """
    Plot the graphs of the two experiments in each directory
    @param dir1: Output files for first experiment
    @param dir2: Output files for first experiment
    @param out_plot: Output dir
    @param hue: Comparison variable for boxplot
    @param how: Compare
    @return:
    """
    if not os.path.isdir(dir1):
        print("{} result directory does not exist.".format(dir1))
    elif not os.path.isdir(dir2):
        print("{} result directory does not exist.".format(dir2))

    df1 = df_from_dir(dir1)
    df1 = df1[df1["Class"] == "B"]
    df2 = df_from_dir(dir2)
    df2 = df2[df2["Class"] == "B"]

    info1 = get_info(os.path.join(dir1, "info.json"))
    info2 = get_info(os.path.join(dir2, "info.json"))

    exp1 = info1["experiment"]
    exp2 = info2["experiment"]
    exp2 = "remove 15 registers"
    df2["Experiment"] = exp2
    flag = info1["flag"]

    total_df = df1.append(df2, ignore_index=True)
    # total_df.sort_values(by=['Benchmark', 'Class', 'Threads', 'Iteration'], inplace=True)
    df1.sort_values(
        by=["Benchmark", "Class", "Threads", "Iteration"], inplace=True
    )
    df1 = df1.reset_index(drop=True)
    df2.sort_values(
        by=["Benchmark", "Class", "Threads", "Iteration"], inplace=True
    )
    df2 = df2.reset_index(drop=True)
    df = pd.DataFrame(df1)
    df["% Overhead"] = df["Time"].combine(
        df2["Time"], lambda x1, x2: (x2 / x1 - 1) * 100
    )
    for bench in set(df["Benchmark"]):
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        sns.set_context(
            rc={"font.size": 14, "axes.titlesize": 24, "axes.labelsize": 16}
        )
        # sns.boxplot(x='Threads', y='Time', hue='Experiment',
        #             data=total_df[(total_df['Benchmark'] == bench)],
        #             palette='Set3')
        sns.stripplot(
            x="Threads",
            y="Time",
            hue="Experiment",
            data=total_df[(total_df["Benchmark"] == bench)],
            size=6,
            color=".3",
            linewidth=0,
            palette="Set1",
        )
        plt.legend(loc=1, prop={"size": 8})
        plt.ylabel("Time (s)")
        plt.legend(fontsize="medium", title_fontsize="20")
        plt.subplot(1, 2, 2)
        sns.set_context(
            rc={"font.size": 14, "axes.titlesize": 24, "axes.labelsize": 16}
        )
        sns.boxplot(
            x="Threads",
            y="% Overhead",
            hue="Class",
            data=df[(df["Benchmark"] == bench)],
            palette="Set3",
        )
        plt.legend([], [], frameon=False)
        bench_out_plot = "{}_{}".format(out_plot, bench)
        title = '{} - "{}" vs "{}" {}'.format(bench, exp2, exp1, flag)
        plt.suptitle(title)
        plt.savefig(bench_out_plot, bbox_inches="tight")
        plt.show()


if __name__ == "__main__":
    for short_hash in ["d97be7cf96dc"]:
        df_overhead = get_overhead_df(
            "npb/results/c6780392", "npb/results/" + short_hash, arch="aarch64"
        )
        dataframe_to_boxplot(df_overhead, arch="aarch64")
        df_overhead = get_overhead_df(
            "npb/results/c6780392", "npb/results/" + short_hash, arch="x86_64"
        )
        dataframe_to_boxplot(df_overhead, "x86_64")
