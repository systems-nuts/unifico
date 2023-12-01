import argparse
import matplotlib.pyplot as plt

from npb.plot_results import get_overhead_df

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Compare NPB results for two different LLVM versions, with one "
        "being the baseline."
    )

    arg_parser.add_argument(
        "baseline_dir", type=str, help="path for baseline result directory"
    )

    arg_parser.add_argument(
        "test_dir", type=str, help="path for test result directory"
    )

    arg_parser.add_argument(
        "-a",
        "--archs",
        required=False,
        help="delimited list of architectures",
        type=str,
        default="aarch64,x86_64",
    )

    arg_parser.add_argument(
        "-c",
        "--npb_class",
        required=False,
        help="NPB class to examine",
        type=str,
        default="B",
    )

    arg_parser.add_argument(
        "-o", "--out_file", required=False, help="Output csv file", type=str
    )

    arg_parser.add_argument("-p", "--plot", action="store_true")

    args = arg_parser.parse_args()

    for arch in args.archs.split(","):
        df_overhead = get_overhead_df(
            args.baseline_dir, args.test_dir, arch, args.npb_class
        )
        print("Experiment: {}".format(df_overhead["Experiment"][0]))
        df_overhead.drop(["Experiment"], axis=1, inplace=True)
        print("NPB overheads for architecture {}".format(arch))
        print(df_overhead)
        print("----------------")

        if args.plot:
            df_overhead.plot(
                x="Benchmark",
                y="% Overhead",
                kind="bar",
                rot=45,
                colormap="Paired",
                title="Overhead compared to baseline - Class B - {}".format(
                    arch
                ),
            )
            plt.show()
