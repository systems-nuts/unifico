import pandas as pd
import os
import json

import matplotlib.pyplot as plt

import seaborn as sns

BENCHMARK_NUM = 10
INFO_FILE = "info.json"


def get_info(json_path):
    """
    Extract info from json file
    @param json_path:
    @return:
    """
    with open(json_path, "r") as fp:
        d = json.load(fp)
    return d


def df_from_file(csv_path, start_line, iterations):
    """
    Extract DataFrame from SPEC results csv
    @param csv_path:
    @param experiment: Short title
    @param start_line: Start of csv line for the result csv
    @param iterations:
    @return:
    """
    nrows = BENCHMARK_NUM * iterations
    df = pd.read_csv(csv_path, skiprows=start_line - 1, nrows=nrows)
    df = df.dropna(subset=["Est. Base Run Time"])
    df["Base # Threads"] = df["Base # Threads"].astype(int)
    return df


def df_from_dir(result_dir, start_line, iterations):
    """
    Extract DataFrame from multiple SPEC results csv in a directory.
    @param result_dir: Directory containing multiple csvs from SPEC runs
    @param start_line: Start of csv line for the result csv
    @param iterations:
    @return:
    """
    df_list = []
    for folder in os.listdir(result_dir):
        folder_path = os.path.join(result_dir, folder)
        if not os.path.isdir(folder_path):
            continue
        for csv in os.listdir(folder_path):
            csv_path = os.path.join(folder_path, csv)
            df = df_from_file(csv_path, start_line, iterations)
            df["Execution Info"] = folder
            df_list.append(df)

    df = pd.concat(
        df_list, ignore_index=True
    )  # Results for all the experiments

    experiment_info = get_info(os.path.join(result_dir, INFO_FILE))
    df["Experiment"] = experiment_info["experiment"]
    df["Flags"] = experiment_info["flags"]

    return df


def plot_core_vs_thread(core_csv_dir, thread_csv_dir, exp, out_plot):
    """
    Plot SPEC core vs threads experiment (compact vs scattered affinity).
    @param core_csv_dir:
    @param thread_csv_dir:
    @param exp: Short title
    @param out_plot:
    @return:
    """
    df_core = df_from_dir(core_csv_dir, exp, 7, 1)
    df_thread = df_from_dir(thread_csv_dir, exp, 7, 1)

    for bench in set(df_core["Benchmark"]):
        plt.subplot(1, 2, 1)
        sns.boxplot(
            x="Base # Threads",
            y="Est. Base Run Time",
            hue="Experiment",
            data=df_core[(df_core["Benchmark"] == bench)],
            palette="Set3",
        )
        plt.legend(loc=1, prop={"size": 8})
        plt.title(bench)

        plt.subplot(1, 2, 2)
        sns.boxplot(
            x="Base # Threads",
            y="Est. Base Run Time",
            hue="Experiment",
            data=df_thread[(df_thread["Benchmark"] == bench)],
            palette="Set3",
        )
        plt.legend(loc=1, prop={"size": 8})
        plt.xticks(rotation=45)
        plt.title(bench)
        plt.savefig(out_plot, bbox_inches="tight")
        plt.show()


def serial_experiments_overhead(df1, df2, out_plot="reports/plots/temp"):
    """
    Plot two SPEC serial experiments over some benchmarks.
    @param df1: Pandas Dataframe with the first experiment results
    @param df2: Pandas Dataframe with the second experiment results
    @param out_plot: Output dir
    """
    df1 = df1[df1["Base # Threads"] == 1]
    df2 = df2[df2["Base # Threads"] == 1]

    df1.sort_values(by=["Benchmark"], inplace=True)
    df1 = df1.reset_index(drop=True)
    df2.sort_values(by=["Benchmark"], inplace=True)
    df2 = df2.reset_index(drop=True)
    total_df = df1.append(df2, ignore_index=True)

    exp1 = df1["Experiment"].iloc[0]
    exp2 = df2["Experiment"].iloc[0]
    flag = df1["Flags"].iloc[0]

    df1 = df1.groupby(["Benchmark"], as_index=False).mean()
    df2 = df2.groupby(["Benchmark"], as_index=False).mean()
    df = pd.DataFrame(df1)
    df["% Overhead"] = df["Est. Base Run Time"].combine(
        df2["Est. Base Run Time"], lambda x1, x2: (x2 / x1 - 1) * 100
    )

    title = "{}: {} overhead to {} {}".format(
        "Serial Benchmarks", exp2, exp1, flag
    )

    fig, axes = plt.subplots(nrows=1, ncols=2)
    plt.figure(figsize=(8, 5))

    # First subplot
    sns.boxplot(
        x="Benchmark",
        y="Est. Base Run Time",
        hue="Experiment",
        data=total_df,
        palette="Set3",
        ax=axes[0],
    )
    plt.sca(axes[0])
    plt.xticks(rotation=45)
    plt.legend(loc=0, prop={"size": 8})

    # Second subplot
    sns.boxplot(
        x="Benchmark", y="% Overhead", data=df, palette="Set3", ax=axes[1]
    )
    plt.sca(axes[1])
    plt.xticks(rotation=45)
    plt.legend(loc=1, prop={"size": 6})

    plt.suptitle(title)
    flag = flag.replace("-", "")
    out_file = "{}_serial_{}".format(out_plot, flag)
    plt.savefig(out_file, bbox_inches="tight")
    plt.show()


def parallel_experiments_overhead(df1, df2, out_plot="reports/plots/temp"):
    """
    Plot two SPEC serial experiments over some benchmarks.
    @param df1: Pandas Dataframe with the first experiment results
    @param df2: Pandas Dataframe with the second experiment results
    @param out_plot: Output dir
    """
    df1 = df1[df1["Execution Info"] == "core"]  # TODO add more cases
    df2 = df2[df2["Execution Info"] == "core"]

    df1.sort_values(by=["Benchmark", "Base # Threads"], inplace=True)
    df1 = df1.reset_index(drop=True)
    df2.sort_values(by=["Benchmark", "Base # Threads"], inplace=True)
    df2 = df2.reset_index(drop=True)
    total_df = df1.append(df2, ignore_index=True)

    exp1 = df1["Experiment"].iloc[0]
    exp2 = df2["Experiment"].iloc[0]
    flag = df1["Flags"].iloc[0]

    df1 = df1.groupby(["Benchmark", "Base # Threads"], as_index=False).mean()
    df2 = df2.groupby(["Benchmark", "Base # Threads"], as_index=False).mean()
    df = pd.DataFrame(df1)
    df["% Overhead"] = df["Est. Base Run Time"].combine(
        df2["Est. Base Run Time"], lambda x1, x2: (x2 / x1 - 1) * 100
    )

    for bench in set(df["Benchmark"]):
        title = "{}: {} overhead to {} {}".format(bench, exp2, exp1, flag)

        fig, axes = plt.subplots(nrows=1, ncols=2)

        # First subplot
        sns.boxplot(
            x="Base # Threads",
            y="Est. Base Run Time",
            hue="Experiment",
            data=total_df,
            palette="Set3",
            ax=axes[0],
        )
        plt.sca(axes[0])
        plt.xticks(rotation=45)
        plt.legend(loc=0, prop={"size": 8})

        # Second subplot
        sns.boxplot(
            x="Base # Threads",
            y="% Overhead",
            data=df,
            palette="Set3",
            ax=axes[1],
        )
        plt.sca(axes[1])
        plt.xticks(rotation=45)
        plt.legend(loc=1, prop={"size": 6})

        plt.suptitle(title)
        bench = bench.replace(".", "")
        bench = bench.replace("_", "")
        flag = flag.replace("-", "")
        out_file = "{}_parallel_{}_{}".format(out_plot, bench, flag)
        plt.savefig(out_file, bbox_inches="tight")
        plt.show()


def compare_experiments(dir1, dir2, out_plot):
    """
    Compare SPEC experiments
    @param dir1:
    @param dir2:
    @param out_plot:
    @return:
    """
    df1 = df_from_dir(dir1, 7, 3)
    df2 = df_from_dir(dir2, 7, 2)
    serial_experiments_overhead(df1, df2, out_plot)
    # parallel_experiments_overhead(df1, df2, out_plot)


def compare_parallel_experiments(
    core_csv_dir1,
    core_csv_dir2,
    thread_csv_dir1,
    thread_csv_dir2,
    exp1,
    exp2,
    out_plot,
):
    """
    Plot SPEC core vs threads experiment (compact vs scattered affinity).
    @param core_csv_dir1:
    @param core_csv_dir2:
    @param thread_csv_dir1:
    @param thread_csv_dir2:
    @param exp1:
    @param exp2:
    @param out_plot: Output dir
    @return:
    """
    df_core1 = df_from_dir(core_csv_dir1, exp1, 7, 3)
    df_core2 = df_from_dir(core_csv_dir2, exp2, 7, 3)
    df_core = pd.concat(
        [df_core1, df_core2], ignore_index=True
    )  # Results for all the experiments

    # df_thread1 = df_from_dir(thread_csv_dir1, exp1, 7, 1)
    # df_thread2 = df_from_dir(thread_csv_dir2, exp2, 7, 1)
    # df_thread = pd.concat([df_thread1, df_thread2], ignore_index=True)  # Results for all the experiments

    for bench in set(df_core["Benchmark"]):
        plt.subplot(1, 2, 1)
        sns.boxplot(
            x="Base # Threads",
            y="Est. Base Run Time",
            hue="Experiment",
            data=df_core[(df_core["Benchmark"] == bench)],
            palette="Set3",
        )
        plt.legend(loc=1, prop={"size": 8})
        plt.title(bench)

        plt.subplot(1, 2, 2)
        # sns.boxplot(x='Base # Threads', y='Est. Base Run Time', hue='Experiment',
        #             data=df_thread[(df_thread['Benchmark'] == bench)],
        #             palette='Set3')
        plt.legend(loc=1, prop={"size": 8})
        plt.xticks(rotation=45)
        plt.title(bench)
        plt.savefig(out_plot, bbox_inches="tight")
        plt.show()


if __name__ == "__main__":
    compare_experiments(
        "results/c617fca",
        "results/a6440f8",
        "reports/plots/nettuno_3_reg_to_temp",
    )

    # compare_experiments('results/new_arm_baseline/027_e4b0249',
    #                     'results/new_arm_remove_15/183_adc8c87',
    #                     'reports/plots/new_arm_remove_15')
