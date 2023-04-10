import argparse
import os

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.pyplot import figure

matplotlib.use("Agg")


def plot_scatter_df(file_name, output_name="temp.png", preserve_csv=False):
    df = pd.read_csv(file_name, sep=",")
    if "address" not in list(df):
        print("WARNING: csv empty.")
        return

    df["address"] = df["address"].apply(lambda x: int(x, 16))

    figure(figsize=(10, 8), dpi=80)

    print(f'    Lines before: {len(df["address"])}')
    Q1 = df["address"].quantile(0.25)
    Q3 = df["address"].quantile(0.75)
    q1 = Q1 - 1.5 * (Q3 - Q1)
    q3 = Q3 + 1.5 * (Q3 - Q1)

    df = df[df["address"].between(q1, q3)]
    print(f'    Lines after: {len(df["address"])}')

    fig = plt.plot(df["step"], df["address"], "r,")
    plt.grid(True)
    plt.title("Memory Accesses")
    plt.xlabel("Time Step")
    plt.ylabel("Memory Address")
    plt.savefig(output_name)

    if not preserve_csv:
        os.system(f"rm {file_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot memory accesses tool.")
    parser.add_argument(
        "-f", "--file", required=True, type=argparse.FileType("r")
    )
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        default="memory_accesses.png",
        type=argparse.FileType("w"),
    )
    args = parser.parse_args()

    plot_scatter_df(args.file.name, args.output.name)
