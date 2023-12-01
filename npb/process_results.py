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
    df_results = pd.DataFrame(index=df1.index)
    df_results["{}_overhead".format(column)] = df1[column].combine(
        df2[column], lambda x1, x2: (x2 / x1 - 1) * 100
    )
    df_results["{}_speedup".format(column)] = df1[column].combine(
        df2[column], lambda x1, x2: x1 / x2
    )
    return df_results


if __name__ == "__main__":
    df_unifico_x86 = pd.read_csv(
        "/home/blackgeorge/Documents/phd/unified_abi/npb/runs/experiments/performance-regression/20230619_211239/run/results.csv",
        index_col="benchmark",
    )
    df_vanilla_x86 = pd.read_csv(
        "/home/blackgeorge/Documents/phd/unified_abi/npb/runs/experiments/cgo2024/x86_init_B/run/results.csv",
        index_col="benchmark",
    )

    x86_overhead = combine_dataframes_column(
        df_vanilla_x86, df_unifico_x86, "time_O0"
    )
    print(x86_overhead)

    x86_overhead.to_csv(
        "x86_overhead.csv",
        header=True,
    )

    df_unifico_arm = pd.read_csv(
        "/home/blackgeorge/Documents/phd/unified_abi/npb/runs/experiments/performance-regression/20230619_210656/run/results.csv",
        index_col="benchmark",
    )
    df_vanilla_arm = pd.read_csv(
        "/home/blackgeorge/Documents/phd/unified_abi/npb/runs/experiments/cgo2024/arm_init_B/run/results.csv",
        index_col="benchmark",
    )

    arm_overhead = combine_dataframes_column(
        df_vanilla_arm, df_unifico_arm, "time_O0"
    )
    print(arm_overhead)

    arm_overhead.to_csv(
        "arm_overhead.csv",
        header=True,
    )
