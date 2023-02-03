import numpy
import matplotlib
import argparse

matplotlib.use("Agg")
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
import pandas as pd


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

    df = pd.read_csv(args.file.name, sep=",")

    df["address"] = df["address"].apply(lambda x: int(x, 16))

    figure(figsize=(10, 8), dpi=80)

    fig = plt.plot(df["step"], df["address"], "r,")
    plt.grid(True)
    plt.title("Memory Accesses")
    plt.xlabel("Time Step")
    plt.ylabel("Memory Address")
    plt.savefig(args.output.name)
