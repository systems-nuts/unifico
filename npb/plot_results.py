import pandas as pd
import os
import re

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


def extract_csv(experiment, commit_short_hash):
    """
    Extract from NPB output files.
    :return:
    """
    script_dir = os.getenv('NPB_SCRIPT_DIR')
    results_dir = '{}/results/{}'.format(script_dir, commit_short_hash)

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
        print(bench, bench_class, threads, affinity, iteration)

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
                    print(time)
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
        df['Threads'] = df['Threads'].astype(int)

    output_csv = os.path.join(results_dir, experiment + '.csv')
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
    print(df)
    df1 = df[df['Affinity'] == 'scatter']
    df2 = df[df['Affinity'] == 'compact']
    for bench in set(df['Benchmark']):
        plt.subplot(1, 2, 1)
        sns.boxplot(x='Threads', y='Time', hue='Experiment',
                    data=df1[(df1['Benchmark'] == bench)],
                    palette='Set3')
        plt.title(bench)
        plt.subplot(1, 2, 2)
        sns.boxplot(x='Threads', y='Time', hue='Experiment',
                    data=df2[(df2['Benchmark'] == bench)],
                    palette='Set3')
        plt.title(bench)
        plt.show()


if __name__ == '__main__':

    csv = extract_csv('baseline', '2f63b22')
    df = pd.read_csv(csv)
    # dataframe_to_boxplot(df)
    two_dataframes_boxplot(df, df)
