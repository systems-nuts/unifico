import pandas as pd
import os
import re
import json

import matplotlib.pyplot as plt

import seaborn as sns


def get_info(json_path):
    """
    Extract experiment info from json file
    @param json_path:
    @return:
    """
    with open(json_path, 'r') as fp:
        d = json.load(fp)
    return d


def verify_npb_output(out_path):
    """
    Verify that npb output file includes a successful run
    @param out_path: npb output file path
    :return: boolean
    """
    with open(out_path, 'r') as fp:
        for line in fp:
            if re.search(r'Verification\s+=\s+SUCCESSFUL', line):
                return True
        return False


# TODO: tests
def df_from_dir(results_dir):
    """
    Extract DataFrame from multiple NPB results in a directory.
    @param results_dir: Directory containing multiple csvs from SPEC runs
    @return:
    """
    info_dict_path = '{}/info.json'.format(results_dir)
    if not os.path.isfile(info_dict_path):
        print('info.json not found')
        exit(1)

    with open(info_dict_path, 'r') as fp:
        info_dict = json.load(fp)
    experiment = info_dict['experiment']
    flag = info_dict['flag']

    df = pd.DataFrame()

    for output in os.listdir(results_dir):
        pattern = re.compile(r'([a-z][a-z])\.([A-Z])_out\.(\d+)\.(compact|scatter)\.(\d+)')
        match = pattern.search(output)
        if match is None:
            continue
        bench = match.group(1)
        bench_class = match.group(2)
        threads = match.group(3)
        affinity = match.group(4)
        iteration = match.group(5)

        output_abs_path = os.path.join(results_dir, output)

        with open(output_abs_path, 'r') as fp:
            verified = False
            verification_pattern = re.compile(r'Verification\s+=\s+SUCCESSFUL')
            time_pattern = re.compile(r'Time in seconds\s+=\s+(\d+\.\d+)')
            for line in fp:
                if verification_pattern.search(line):
                    verified = True
                match = time_pattern.search(line)
                if match is not None:
                    time = match.group(1)
            if not verified:
                print('Not verified: ', output)
                exit(1)

        out_dict = {
            'Experiment': experiment,
            'Flag': flag,
            'Benchmark': bench,
            'Class': bench_class,
            'Threads': int(threads),
            'Affinity': affinity,
            'Iteration': int(iteration),
            'Time': float(time)
        }

        df = df.append(out_dict, ignore_index=True)

    df['Threads'] = df['Threads'].astype(int)

    return df


def dataframe_to_catplot(df):
    """
    @param df: Pandas DataFrame
    """
    for bench in set(df['Benchmark']):
        sns.catplot(x='Threads', y='Time', hue='Experiment', col='Affinity',
                    data=df[(df['Benchmark'] == bench)], kind='box',
                    palette='Set3')
        plt.title(bench)
        plt.ylabel('Time (s)')
        plt.show()


def dataframe_to_boxplot(df, hue='Experiment'):
    """
    @param df: Pandas DataFrame
    @param hue: Comparison variable for boxplot
    """
    for bench in set(df['Benchmark']):
        sns.boxplot(x='Threads', y='Time', hue=hue,
                    data=df[(df['Benchmark'] == bench)],
                    palette='Set3')
        plt.title(bench)
        plt.ylabel('Time (s)')
        plt.show()


def two_dataframes_boxplot(df1, df2):
    """
    @param df1: Pandas Dataframe
    @param df2: Pandas Dataframe
    """
    df = df1.append(df2, ignore_index=True)

    df1 = df[df['Affinity'] == 'scatter']
    df2 = df[df['Affinity'] == 'compact']
    for bench in set(df['Benchmark']):
        plt.subplot(1, 2, 1)
        sns.boxplot(x='Threads', y='Time', hue='Experiment',
                    data=df1[(df1['Benchmark'] == bench)],
                    palette='Set3')
        plt.legend(loc=1, prop={'size': 8})
        plt.title(bench)
        plt.subplot(1, 2, 2)
        sns.boxplot(x='Threads', y='Time', hue='Experiment',
                    data=df2[(df2['Benchmark'] == bench)],
                    palette='Set3')
        plt.legend(loc=1, prop={'size': 8})
        plt.title(bench)
        plt.savefig(bench)
        plt.show()


def compare_experiments(dir1, dir2, out_plot, hue='Experiment', how='side'):
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
        print('{} result directory does not exist.'.format(dir1))
    elif not os.path.isdir(dir2):
        print('{} result directory does not exist.'.format(dir2))

    df1 = df_from_dir(dir1)
    df1 = df1[df1['Class'] == 'B']
    df2 = df_from_dir(dir2)
    df2 = df2[df2['Class'] == 'B']

    info1 = get_info(os.path.join(dir1, 'info.json'))
    info2 = get_info(os.path.join(dir2, 'info.json'))

    exp1 = info1['experiment']
    exp2 = info2['experiment']
    exp2 = 'remove 15 registers'
    df2['Experiment'] = exp2
    flag = info1['flag']

    total_df = df1.append(df2, ignore_index=True)
    # total_df.sort_values(by=['Benchmark', 'Class', 'Threads', 'Iteration'], inplace=True)
    df1.sort_values(by=['Benchmark', 'Class', 'Threads', 'Iteration'], inplace=True)
    df1 = df1.reset_index(drop=True)
    df2.sort_values(by=['Benchmark', 'Class', 'Threads', 'Iteration'], inplace=True)
    df2 = df2.reset_index(drop=True)
    df = pd.DataFrame(df1)
    df['% Overhead'] = df['Time'].combine(df2['Time'], lambda x1, x2: (x2 / x1 - 1) * 100)
    for bench in set(df['Benchmark']):
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        sns.set_context(rc={"font.size": 14, "axes.titlesize": 24, "axes.labelsize": 16})
        # sns.boxplot(x='Threads', y='Time', hue='Experiment',
        #             data=total_df[(total_df['Benchmark'] == bench)],
        #             palette='Set3')
        sns.stripplot(x='Threads', y='Time', hue='Experiment',
                      data=total_df[(total_df['Benchmark'] == bench)],
                      size=6, color=".3", linewidth=0,
                      palette='Set1')
        plt.legend(loc=1, prop={'size': 8})
        plt.ylabel('Time (s)')
        plt.legend(fontsize='medium', title_fontsize='20')
        plt.subplot(1, 2, 2)
        sns.set_context(rc={"font.size": 14, "axes.titlesize": 24, "axes.labelsize": 16})
        sns.boxplot(x='Threads', y='% Overhead', hue='Class',
                        data=df[(df['Benchmark'] == bench)],
                        palette='Set3')
        plt.legend([], [], frameon=False)
        bench_out_plot = '{}_{}'.format(out_plot, bench)
        title = '{} - "{}" vs "{}" {}'.format(bench, exp2, exp1, flag)
        plt.suptitle(title)
        plt.savefig(bench_out_plot, bbox_inches='tight')
        plt.show()


if __name__ == '__main__':
    compare_experiments('results/1496895', 'results/remove_14_regs/ca1f7d6',
                        'reports/plots/sole_remove_15_O1_B_large_font', hue='Class', how='overhead')
