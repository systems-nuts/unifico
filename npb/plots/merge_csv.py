import argparse
import pandas as pd


def merge_csv_files(output_filename, *input_files):
    # Initialize an empty DataFrame to store the merged data
    merged_df = None

    for file in input_files:
        # Read each input CSV file into a DataFrame
        df = pd.read_csv(file)

        if "time_speedup" in df.columns:
            df = df.drop(columns=["time_speedup"])
        df = df.drop(df[df["benchmark"] == "Geomean"].index)

        # Merge the data side by side using the common column
        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on="benchmark", how="outer")

    # Sort the DataFrame by index
    merged_df.sort_index(inplace=True)

    # Save the merged DataFrame to a new CSV file
    merged_df.to_csv(output_filename, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Merge multiple CSV files into a single CSV file"
    )
    parser.add_argument("output", help="output CSV file")
    parser.add_argument("inputs", nargs="+", help="input CSV files")
    args = parser.parse_args()

    merge_csv_files(args.output, *args.inputs)
