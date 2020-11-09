import pandas as pd
import os
import re
import json

import matplotlib.pyplot as plt

import seaborn as sns


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


def extract_csv(commit_short_hash):
    """
    Extract from NPB output files.
    :return:
    """
    script_dir = os.getenv('NPB_SCRIPT_DIR')
    results_dir = '{}/results/{}'.format(script_dir, commit_short_hash)

    info_dict_path = '{}/info.json'.format(results_dir)
    if not os.path.isfile(info_dict_path):
        print('info.json not found')
        exit(1)

    with open(info_dict_path, 'r') as fp:
        info_dict = json.load(fp)
    experiment = info_dict['experiment']

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
            'Benchmark': bench,
            'Class': bench_class,
            'Threads': int(threads),
            'Affinity': affinity,
            'Iteration': int(iteration),
            'Time': float(time)
        }

        df = df.append(out_dict, ignore_index=True)

    output_csv = os.path.join(results_dir, commit_short_hash + '.csv')
    df['Threads'] = df['Threads'].astype(int)
    df.to_csv(output_csv, index=False)

    return output_csv


def dataframe_to_boxplot(df):
    """
    @param df: Pandas DataFrame
    """
    for bench in set(df['Benchmark']):
        sns.boxplot(x='Threads', y='Time', hue='Affinity',
                    data=df[(df['Benchmark'] == bench)],
                    palette='Set3')
        plt.title(bench)
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


def compare_experiments(hash1, hash2):
    """
    Plot the graphs of the two experiments
    @param hash1: git commit short hash corresponding to first experiment
    @param hash2: git commit short hash corresponding to second experiment
    @return:
    """
    script_dir = os.getenv('NPB_SCRIPT_DIR')
    results_dir = '{}/results'.format(script_dir)
    os.chdir(results_dir)

    if not os.path.isdir(hash1):
        print('{} result directory does not exist.'.format(hash1))
    elif not os.path.isdir(hash2):
        print('{} result directory does not exist.'.format(hash2))

    csv1 = os.path.join(hash1, hash1 + '.csv')
    csv2 = os.path.join(hash2, hash2 + '.csv')

    if not os.path.isfile(csv1):
        extract_csv(hash1)
    if not os.path.isfile(csv2):
        extract_csv(hash2)

    df1 = pd.read_csv(csv1)
    df2 = pd.read_csv(csv2)
    two_dataframes_boxplot(df1, df2)


if __name__ == '__main__':
    compare_experiments('fbbec41', '0e1e380')
