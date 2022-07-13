import pytest
import pandas as pd

from npb.plot_results import df_from_dir, get_overhead_df

COLUMNS = [
    "Experiment",
    "Flag",
    "Benchmark",
    "Architecture",
    "Class",
    "Iteration",
    "Time",
]


def test_df_from_dir_correct():
    """
    Test whether this function successfully creates a Dataframe out of the npb results in a directory.
    """
    target_df = pd.DataFrame(
        [
            ["modified", "-O1", "bt", "x86_64", "B", 1, 295.85],
            ["modified", "-O1", "ep", "x86_64", "B", 2, 118.65],
            ["modified", "-O1", "bt", "x86_64", "B", 2, 295.44],
            ["modified", "-O1", "ep", "x86_64", "B", 1, 118.36],
            ["modified", "-O1", "ep", "x86_64", "B", 3, 118.36],
            ["modified", "-O1", "bt", "x86_64", "B", 3, 295.36],
        ],
        columns=COLUMNS,
    )

    df = df_from_dir("npb/test/results/correct")

    pd.testing.assert_frame_equal(
        target_df, df, check_like=True, check_less_precise=2, check_dtype=False
    ), "Dataframes are not equal!!"


def test_df_from_dir_no_json():
    """
    Test whether this function successfully creates a Dataframe out of the npb results in a directory.
    If no `info.json` file is given, the name of the folder must be used as the experiment name.
    """
    df = df_from_dir("npb/test/results/no_json")

    target_df = pd.DataFrame(
        [
            ["no_json", "", "bt", "x86_64", "B", 1, 295.85],
            ["no_json", "", "ep", "x86_64", "B", 2, 118.65],
            ["no_json", "", "bt", "x86_64", "B", 2, 295.44],
            ["no_json", "", "ep", "x86_64", "B", 1, 118.36],
            ["no_json", "", "ep", "x86_64", "B", 3, 118.36],
            ["no_json", "", "bt", "x86_64", "B", 3, 295.36],
        ],
        columns=COLUMNS,
    )

    pd.testing.assert_frame_equal(
        target_df, df, check_like=True, check_less_precise=2, check_dtype=False
    ), "Dataframes are not equal!!"


def test_df_from_dir_unverified():
    """
    Test whether this function successfully creates a Dataframe out of the npb results in a directory.
    If a file is not verified, then NaN must be stored as the result.
    """
    df = df_from_dir("npb/test/results/unverified")

    target_df = pd.DataFrame(
        [
            ["unmodified", "-O1", "bt", "x86_64", "B", 1, 295.85],
            ["unmodified", "-O1", "ep", "x86_64", "B", 2, float("nan")],
            ["unmodified", "-O1", "bt", "x86_64", "B", 2, 295.44],
            ["unmodified", "-O1", "ep", "x86_64", "B", 1, float("nan")],
            ["unmodified", "-O1", "ep", "x86_64", "B", 3, float("nan")],
            ["unmodified", "-O1", "bt", "x86_64", "B", 3, 295.36],
        ],
        columns=COLUMNS,
    )

    pd.testing.assert_frame_equal(
        target_df, df, check_like=True, check_less_precise=2, check_dtype=False
    ), "Dataframes are not equal!!"


def test_get_overhead_df():
    """
    Test whether this function successfully creates a Dataframe with the time overhead between two different
    dataframes, from given directories.
    If a value is NaN, the overhead result is NaN.
    """
    df = get_overhead_df(
        "npb/test/results/correct", "npb/test/results/correct2"
    )

    target_df = pd.DataFrame(
        [
            ["unmodified", "-O1", "bt", "x86_64", "B", 1, 295.85],
            ["unmodified", "-O1", "ep", "x86_64", "B", 2, float("nan")],
            ["unmodified", "-O1", "bt", "x86_64", "B", 2, 295.44],
            ["unmodified", "-O1", "ep", "x86_64", "B", 1, float("nan")],
            ["unmodified", "-O1", "ep", "x86_64", "B", 3, float("nan")],
            ["unmodified", "-O1", "bt", "x86_64", "B", 3, 295.36],
        ],
        columns=COLUMNS,
    )

    pd.testing.assert_frame_equal(
        target_df, df, check_like=True, check_less_precise=2, check_dtype=False
    ), "Dataframes are not equal!!"
