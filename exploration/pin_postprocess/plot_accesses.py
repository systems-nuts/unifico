import argparse
import os

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.pyplot import figure

matplotlib.use("Agg")


def onedim_cluster(df):
    eps = int(0x1000000)
    min_samples = 200
    clusters = []
    df = df.sort_values("address")
    address = list(df["address"])
    step = list(df["step"])
    points_sorted = list(zip(address, step))
    curr_point = points_sorted[0]
    curr_cluster = [curr_point]
    for point in points_sorted[1:]:
        if point[0] <= curr_point[0] + eps:
            curr_cluster.append(point)
        else:
            if len(curr_cluster) > min_samples:
                clusters.append(curr_cluster)
            curr_cluster = [point]
        curr_point = point
    if len(curr_cluster) > min_samples:
        clusters.append(curr_cluster)
    return clusters


def filter_df(df):
    """
    Remove outliers from the dataframe.
    :param df:
    :return:
    """
    lines_before = len(df["address"])

    first_quantile = df["address"].quantile(0.25)
    third_quantile = df["address"].quantile(0.75)
    q1 = first_quantile - 1.5 * (third_quantile - first_quantile)
    q3 = third_quantile + 1.5 * (third_quantile - first_quantile)
    df = df[df["address"].between(q1, q3)]

    lines_after = len(df["address"])
    filtered_lines = lines_before - lines_after
    if filtered_lines:
        print(f"    filtered: {filtered_lines} lines")
    return df


def scatter_plot_df(
    df, x_label="x", y_label="y", title="Scatter Plot", output_name="temp.png"
):
    """
    Scatter-plots the dataframe in a raster graph.
    :param x_label:
    :param y_label:
    :param title:
    :param output_name:
    :param df:
    :return:
    """
    figure(figsize=(10, 8), dpi=80)
    plt.plot(df["step"], df["address"], "r,")
    plt.grid(True)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.savefig(output_name)
    plt.clf()


def scatter_csv_plot(file_name, output_name="temp.png", preserve_csv=False):
    df = pd.read_csv(file_name, sep=",")
    if "address" not in list(df):
        print("WARNING: wrong csv format.")
        return

    df["address"] = df["address"].apply(lambda x: int(x, 16))

    # Plot the whole csv into a file
    df = filter_df(df)
    full_img_output = output_name.replace(".png", ".full.png")
    scatter_plot_df(
        df, "Time Step", "Memory Addresses", "Memory Accesses", full_img_output
    )

    clusters = onedim_cluster(df)

    # Plot each cluster of the csv into separate files
    cluster_id = 0
    for cluster in clusters:
        cluster_data = pd.DataFrame(cluster, columns=["address", "step"])
        cluster_img_output = output_name.replace(".png", f".{cluster_id}.png")
        scatter_plot_df(
            cluster_data,
            "Time Step",
            "Memory Addresses",
            "Memory Accesses",
            cluster_img_output,
        )
        cluster_id += 1

    if not preserve_csv:
        os.system(f"rm {file_name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot memory accesses tool.")
    parser.add_argument("-f", "--file", required=True, type=str)
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        default="memory_accesses.png",
        type=str,
    )
    args = parser.parse_args()

    scatter_csv_plot(args.file, args.output, preserve_csv=True)
