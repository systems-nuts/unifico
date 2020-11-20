import pandas as pd
import os

import matplotlib.pyplot as plt

import seaborn as sns

# TODO: export benchmark number as constant?


def df_from_file(csv_path, experiment, start_line, benchmark_num, iterations):
    """
    Extract DataFrame from SPEC results csv
    @param csv_path:
    @param experiment: Short title
    @param start_line: Start of csv line for the result csv
    @param benchmark_num: How many benchmarks run
    @param iterations:
    @return:
    """
    nrows = benchmark_num * iterations
    df = pd.read_csv(csv_path, skiprows=start_line - 1, nrows=nrows)
    df = df.dropna(subset=['Est. Base Run Time'])
    df['Experiment'] = pd.Series([experiment] * nrows)
    df['Base # Threads'] = df['Base # Threads'].astype(int)
    return df


def df_from_dir(results_dir, experiment, start_line, benchmark_num, iterations):
    """
    Extract DataFrame from multiple SPEC results csv in a directory.
    @param results_dir: Directory containing multiple csvs from SPEC runs
    @param experiment: Short title
    @param start_line: Start of csv line for the result csv
    @param benchmark_num: How many benchmarks run
    @param iterations:
    @return:
    """
    df_list = []
    for csv in os.listdir(results_dir):
        csv_path = os.path.join(results_dir, csv)
        df = df_from_file(csv_path, experiment, start_line, benchmark_num, iterations)
        df_list.append(df)

    df = pd.concat(df_list, ignore_index=True)  # Results for all the experiments
    return df


def plot_serial(csv, exp, out_plot):
    """
    Plot two SPEC serial experiments over some benchmarks.
    @param csv: path to first csv
    @param exp: first experiment name
    @param out_plot:
    @return:
    """
    df = df_from_file(csv, exp, 7, 10, 3)
    sns.boxplot(x='Benchmark', y='Est. Base Run Time', hue='Experiment',
                data=df, palette='Set3')
    plt.legend(loc=1, prop={'size': 8})
    plt.title('Serial Benchmarks')
    plt.savefig(out_plot, bbox_inches='tight')
    plt.show()


def compare_serial_experiments(csv1, exp1, csv2, exp2, out_plot):
    """
    Plot two SPEC serial experiments over some benchmarks.
    @param csv1: path to first csv
    @param exp1: first experiment name
    @param csv2: path to second csv
    @param exp2: second experiment name
    @param out_plot:
    @return:
    """
    df1 = df_from_file(csv1, exp1, 7, 10, 1)
    df2 = df_from_file(csv2, exp2, 7, 10, 3)

    df = df1.append(df2, ignore_index=True)

    sns.boxplot(x='Benchmark', y='Est. Base Run Time', hue='Experiment',
                data=df, palette='Set3')
    plt.legend(loc=1, prop={'size': 8})
    plt.title('Serial Benchmarks')
    plt.savefig(out_plot, bbox_inches='tight')
    plt.show()


def plot_core_vs_thread(core_csv_dir, thread_csv_dir, exp, out_plot):
    """
    Plot SPEC core vs threads experiment (compact vs scattered affinity).
    @param core_csv_dir:
    @param thread_csv_dir:
    @param exp: Short title
    @param out_plot:
    @return:
    """
    df_core = df_from_dir(core_csv_dir, exp, 7, 10, 1)
    df_thread = df_from_dir(thread_csv_dir, exp, 7, 10, 1)

    for bench in set(df_core['Benchmark']):
        plt.subplot(1, 2, 1)
        sns.boxplot(x='Base # Threads', y='Est. Base Run Time', hue='Experiment',
                    data=df_core[(df_core['Benchmark'] == bench)],
                    palette='Set3')
        plt.legend(loc=1, prop={'size': 8})
        plt.title(bench)

        plt.subplot(1, 2, 2)
        sns.boxplot(x='Base # Threads', y='Est. Base Run Time', hue='Experiment',
                    data=df_thread[(df_thread['Benchmark'] == bench)],
                    palette='Set3')
        plt.legend(loc=1, prop={'size': 8})
        plt.xticks(rotation=45)
        plt.title(bench)
        plt.savefig(out_plot, bbox_inches='tight')
        plt.show()


def compare_parallel_experiments(core_csv_dir1, core_csv_dir2, thread_csv_dir1, thread_csv_dir2,
                                 exp1, exp2, out_plot):
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
    df_core1 = df_from_dir(core_csv_dir1, exp1, 7, 10, 3)
    df_core2 = df_from_dir(core_csv_dir2, exp2, 7, 10, 1)
    df_core = pd.concat([df_core1, df_core2], ignore_index=True)  # Results for all the experiments

    df_thread1 = df_from_dir(thread_csv_dir1, exp1, 7, 10, 3)
    df_thread2 = df_from_dir(thread_csv_dir2, exp2, 7, 10, 1)
    df_thread = pd.concat([df_thread1, df_thread2], ignore_index=True)  # Results for all the experiments

    for bench in set(df_core['Benchmark']):
        plt.subplot(1, 2, 1)
        sns.boxplot(x='Base # Threads', y='Est. Base Run Time', hue='Experiment',
                    data=df_core[(df_core['Benchmark'] == bench)],
                    palette='Set3')
        plt.legend(loc=1, prop={'size': 8})
        plt.title(bench)

        plt.subplot(1, 2, 2)
        sns.boxplot(x='Base # Threads', y='Est. Base Run Time', hue='Experiment',
                    data=df_thread[(df_thread['Benchmark'] == bench)],
                    palette='Set3')
        plt.legend(loc=1, prop={'size': 8})
        plt.xticks(rotation=45)
        plt.title(bench)
        plt.savefig(out_plot, bbox_inches='tight')
        plt.show()


if __name__ == '__main__':
    # plot_serial('results/011_806b233/CPU2017.011.intspeed.refspeed.csv',
    #             'base', 'reports/plots/sole_serial')
    plot_core_vs_thread('results/FIRST_EXP_NUM_{short_hash}/core_run', 'results/FIRST_EXP_NUM_{short_hash}/thread_run',
                        'base', 'reports/plots/sole_parallel_2')
    # compare_serial_experiments('results/451_e32eba4/CPU2017.451.intspeed.refspeed.csv', 'base',
    #                            'results/305_5fdb6d0/CPU2017.305.intspeed.refspeed.csv', 'r13_r14_temp',
    #                            'reports/plots/r13_r14_serial')
    # compare_parallel_experiments('results/451_e32eba4/core_run', 'results/305_5fdb6d0/core_run',
    #                              'results/451_e32eba4/thread_run', 'results/305_5fdb6d0/thread_run',
    #                              'base', 'r12_r13_r14_temp',
    #                              'reports/plots/plot2')
