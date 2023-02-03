import numpy
import matplotlib
import argparse

matplotlib.use("Agg")
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
import pandas as pd


def plot_scatter_df(file_name, output_name="temp.png"):

    df = pd.read_csv(file_name, sep=",")
    df["address"] = df["address"].apply(lambda x: int(x, 16))

    figure(figsize=(10, 8), dpi=80)

    fig = plt.plot(df["step"], df["address"], "r,")
    plt.grid(True)
    plt.title("Memory Accesses")
    plt.xlabel("Time Step")
    plt.ylabel("Memory Address")
    plt.savefig(output_name)


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
