import pandas as pd
import numpy as np

import matplotlib.pyplot as plt


def extract_scores(csv_path, benchmark_num, iterations, start_line):
    """
    Extract statistics for the runtime of a SPEC report.
    :param csv_path: location of csv
    :param benchmark_num:
    :param iterations: parameter of benchmark execution
    :param start_line: beginning of csv
    :return:
    """
    df = pd.read_csv(csv_path, skiprows=start_line - 1, nrows=benchmark_num * iterations)
    benchmark_names = df['Benchmark']
    scores_series = df['Est. Base Run Time']
    scores = list(scores_series.apply(lambda x: float(x)))
    aggregated_scores = [scores[x:x + iterations] for x in range(0, len(scores), iterations)]

    aggregated_scores = np.array(aggregated_scores)
    average_scores = [np.average(x) for x in aggregated_scores]
    min_scores = [np.min(x) for x in aggregated_scores]
    max_scores = [np.max(x) for x in aggregated_scores]
    percentile_scores = [np.percentile(x, 95) for x in aggregated_scores]

    print(benchmark_names)
    print(average_scores)
    print(min_scores)
    print(max_scores)
    print(percentile_scores)


def plot_graph(x_Axis, y):

    x_Axis = [1, 2, 3]
    ipc_Axis = [1, 2, 3]
    mpki_Axis = [1, 2, 3]

    fig, ax1 = plt.subplots()
    ax1.grid(True)
    ax1.set_xlabel("CacheSize.Assoc.BlockSize")

    xAx = np.arange(len(x_Axis))
    ax1.xaxis.set_ticks(np.arange(0, len(x_Axis), 1))
    ax1.set_xticklabels(x_Axis, rotation=45)
    ax1.set_xlim(-0.5, len(x_Axis) - 0.5)
    ax1.set_ylim(min(ipc_Axis) - 0.05 * min(ipc_Axis), max(ipc_Axis) + 0.05 * max(ipc_Axis))
    ax1.set_ylabel("$IPC$")
    line1 = ax1.plot(ipc_Axis, label="ipc", color="red", marker='x')

    ax2 = ax1.twinx()
    ax2.xaxis.set_ticks(np.arange(0, len(x_Axis), 1))
    ax2.set_xticklabels(x_Axis, rotation=45)
    ax2.set_xlim(-0.5, len(x_Axis) - 0.5)
    ax2.set_ylim(min(mpki_Axis) - 0.05 * min(mpki_Axis), max(mpki_Axis) + 0.05 * max(mpki_Axis))
    ax2.set_ylabel("$MPKI$")
    line2 = ax2.plot(mpki_Axis, label="L1D_mpki", color="green", marker='o')

    lns = line1 + line2
    labs = [l.get_label() for l in lns]

    plt.title("IPC vs MPKI")
    lgd = plt.legend(lns, labs)
    lgd.draw_frame(False)
    plt.savefig("L1.png", bbox_inches="tight")


if __name__ == '__main__':

    extract_scores('results/test.csv', 10, 1, 7)
    plot_graph([],[])