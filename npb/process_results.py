import pandas as pd
import numpy as np

from plot_results import df_from_dir
from scipy.stats import gmean

UNIFICO_FOLDER = "results/3bc0695c2a338"
UNMODIFIED_FOLDER = "results/c1a0a21"
EXCEL_PATH = "data/cgo2023.xlsx"
CHRIS_X86_PATH = "data/cgo2023_x86.csv"
CHRIS_ARM_PATH = "data/cgo2023_arm.csv"
OUT_X86_PATH = "data/x86.csv"
OUT_ARM_PATH = "data/arm.csv"


def get_average_time(df):
    df = df.dropna()
    df.drop("Experiment", axis=1, inplace=True)
    df.drop(df[df["Class"] == "S"].index, inplace=True)
    df_sorted = df.sort_values(["Benchmark", "Architecture", "Class"])
    df_grouped = df_sorted.groupby(
        ["Benchmark", "Architecture", "Class"]
    ).mean()
    df_grouped.reset_index(inplace=True)
    df_grouped.drop("Iteration", axis=1, inplace=True)
    df_grouped.drop(["Architecture"], axis=1, inplace=True)
    df_grouped = (
        df_grouped.set_index(["Benchmark", "Class"])
        .stack()
        .unstack(level=1)
        .reset_index()
    )
    df_grouped.drop(["level_1"], axis=1, inplace=True)
    return df_grouped


def combine_dataframes_column(df1, df2, column):
    df_results = pd.DataFrame()
    df_results["{} % Overhead".format(column)] = df1[column].combine(
        df2[column], lambda x1, x2: (x2 / x1 - 1) * 100
    )
    df_results["{} Speedup".format(column)] = df1[column].combine(
        df2[column], lambda x1, x2: x1 / x2
    )
    return df_results


if __name__ == "__main__":

    df_chris_x86 = pd.read_csv(CHRIS_X86_PATH, nrows=4)
    df_chris_arm = pd.read_csv(CHRIS_ARM_PATH, nrows=4)

    df_unifico = df_from_dir(UNIFICO_FOLDER)
    df_unifico_x86 = get_average_time(
        df_unifico[df_unifico["Architecture"] == "x86_64"]
    )
    df_unifico_arm = get_average_time(
        df_unifico[df_unifico["Architecture"] == "aarch64"]
    )

    df_unmodified = df_from_dir(UNMODIFIED_FOLDER)
    df_unmodified_x86 = get_average_time(
        df_unmodified[df_unmodified["Architecture"] == "x86_64"]
    )
    df_unmodified_arm = get_average_time(
        df_unmodified[df_unmodified["Architecture"] == "aarch64"]
    )

    df_results_arm = pd.DataFrame()
    df_results_arm["Benchmark"] = df_unmodified_arm["Benchmark"]

    df_results_x86 = pd.DataFrame()
    df_results_x86["Benchmark"] = df_unmodified_x86["Benchmark"]

    for class_name in ["A", "B", "C"]:

        res = combine_dataframes_column(
            df_unmodified_arm, df_unifico_arm, class_name
        )
        df_results_arm = pd.concat([df_results_arm, res], axis=1)

        res = combine_dataframes_column(
            df_unmodified_x86, df_unifico_x86, class_name
        )
        df_results_x86 = pd.concat([df_results_x86, res], axis=1)

    df_results_x86 = pd.concat([df_results_x86, df_chris_x86], axis=0)
    df_results_arm = pd.concat([df_results_arm, df_chris_arm], axis=0)

    df_results_x86.set_index("Benchmark", inplace=True)
    df_results_arm.set_index("Benchmark", inplace=True)
    # df_results_arm.loc['Geomean'] = df_results_arm[df_results_arm.notna()].apply(gmean, axis=0)
    # df_results_x86.loc['Geomean'] = df_results_x86[df_results_x86.notna()].apply(gmean, axis=0)
    # df_results_x86.loc['Average'] = df_results_x86.mean(axis=0)
    # df_results_arm.loc['Geomean'] = df_results_arm[df_results_arm.notna()].apply(gmean, axis=0)
    # df_results_arm.loc['Average'] = df_results_arm.mean(axis=0)
    with pd.option_context(
        "display.max_rows",
        None,
        "display.max_columns",
        None,
        "display.expand_frame_repr",
        False,
    ):  # more options can be specified also
        print(df_results_arm)
        print(df_results_x86)

    with open(OUT_X86_PATH, "w") as fp:
        df_results_x86.to_csv(fp)
    with open(OUT_ARM_PATH, "w") as fp:
        df_results_arm.to_csv(fp)
