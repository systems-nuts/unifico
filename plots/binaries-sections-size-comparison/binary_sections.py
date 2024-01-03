import matplotlib.pyplot as plt
import pandas as pd
import argparse
import altair as alt
import json
import csv

# COMPILERS = ["clang", "popcorn", "unasl"]
COMPILERS = ["vanilla", "popcorn", "unifico"]
# BENCHMARKS = ["is", "bt", "ft", "cg", "ep"]
BENCHMARKS = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp", "ua"]
SECTIONS = [
    ".text",
    ".data",
    ".rodata",
    ".stack_transform",
    ".stackmaps",
    ".debug",
]


def prep_df(df, name):
    df = df.stack().reset_index()
    df.columns = ["c1", "c2", "values"]
    df["Section"] = name
    return df


def parse_sizes(arch):
    sections = {}
    for compiler in COMPILERS:
        sections[compiler] = {}
        for benchmark in BENCHMARKS:
            sections[compiler][benchmark] = {}
            with open(
                "./10112023/B/o1/"
                + compiler
                + f"/{arch}/"
                + benchmark
                + ".txt",
                "r",
            ) as reader:
                lines = reader.readlines()
                lines = [line.split() for line in lines]
                lines = [
                    line
                    for line in lines
                    if (len(line) > 0 and line[0].startswith("."))
                ]

            sections[compiler][benchmark] = {
                line[0]: int(line[1]) for line in lines
            }

            data = [
                v
                for k, v in sections[compiler][benchmark].items()
                if k.startswith(".data")
            ]
            sections[compiler][benchmark][".data"] = sum(data)

            stack_transform = [
                v
                for k, v in sections[compiler][benchmark].items()
                if k.startswith(".stack_transform")
            ]
            sections[compiler][benchmark][".stack_transform"] = sum(
                stack_transform
            )

            debug = [
                v
                for k, v in sections[compiler][benchmark].items()
                if k.startswith(".debug")
            ]
            sections[compiler][benchmark][".debug"] = sum(debug)

            rodata = [
                v
                for k, v in sections[compiler][benchmark].items()
                if k.startswith(".rodata")
            ]
            sections[compiler][benchmark][".rodata"] = sum(rodata)

            sections[compiler][benchmark][".stackmaps"] = sections[compiler][
                benchmark
            ].get(".llvm_pcn_stackmaps", 0)

            sections[compiler][benchmark] = {
                k: v
                for (k, v) in sections[compiler][benchmark].items()
                if k in SECTIONS
            }

    return sections


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Plot binary sizes.",
    )
    arg_parser.add_argument(
        "-a",
        "--arch",
        required=True,
        const=str,
        nargs="?",
    )
    args = arg_parser.parse_args()
    sizes = parse_sizes(args.arch)

    sections = {}
    merged_df = None
    for section in SECTIONS:
        sections[section] = pd.DataFrame(
            [
                [sizes[compiler][benchmark][section] for compiler in COMPILERS]
                for benchmark in BENCHMARKS
            ],
            index=[name for name in BENCHMARKS],
            columns=[name for name in COMPILERS],
        )
        sections[section] = prep_df(sections[section], section)
        if merged_df is None:
            merged_df = sections[section]
            merged_df[section] = merged_df["values"] / 1000000.0
            merged_df.drop(columns=["values", "Section"], inplace=True)
        else:
            merged_df = pd.merge(
                merged_df, sections[section], on=["c1", "c2"], how="left"
            )
            merged_df[section] = merged_df["values"] / 1000000.0
            merged_df.drop(columns=["values", "Section"], inplace=True)

    df = pd.concat(sections.values())
    # merged_df.drop(columns=['.stackmaps'], inplace=True)
    merged_df.rename(columns={"c1": "bmk", "c2": "class"}, inplace=True)
    merged_df = merged_df[
        ["bmk", "class", ".data", ".rodata", ".debug", ".text"]
    ]

    COLORS = [
        "Gold",
        "LightPink",
        "MidnightBlue",
        "MediumVioletRed",
        "LightSteelBlue",
        "MediumSlateBlue",
    ]
    df = df[df["Section"] != ".stackmaps"]
    df = df.sort_values(["Section"], ascending=[True])
    COLORS = [
        "#ca0020",
        "#f4a582",
        "#ffffff",
        "#bababa",
        "#404040",
    ]

    pattern_scale = {
        "domain": ["Popcorn", "Unifico", "Vanilla"],
        "range": [
            "url(#diagonal_up_left)",
            "url(#cross_hatch)",
            "url(#diagonal_up_right)",
        ],
    }

    # Define your custom hatch patterns
    hatch_patterns = ["-", "|", "/", "\\"]

    # alt.Chart(df).mark_bar().encode(
    #     x=alt.X('c2:N', title=None),
    #     y=alt.Y('sum(values):Q', axis=alt.Axis(grid=False, title="Size")),
    #     column=alt.Column('c1:N', title="Benchmark"),
    #     color=alt.Color('Section:N', scale=alt.Scale(range=COLORS, )),strokeDash=alt.StrokeDash('c2:N', scale=alt.Scale(domain=hatch_patterns))).configure_view(strokeOpacity=0).properties(width=80, height=600).show()

    # print(json.dumps(sizes, indent=4, sort_keys=True))
    with open(
        f"../../npb/data/cc2024/binary_sizes_o1_B_{args.arch}_temp.csv", "w"
    ) as f:  # You will need 'wb' mode in Python 2.x
        merged_df.to_csv(f, index=False)
