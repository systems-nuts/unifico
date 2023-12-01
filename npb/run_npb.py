import argparse
import os
import re

from utilities.system_topology import SystemTopology


def parse_suite(suite_file):
    """
    Simple function to extract info on what NPB benchmarks were compiled and what classes
    :param suite_file: path to file
    :return: list of tuples (benchmark name, class)
    """
    bench_pattern = re.compile("^([a-z][a-z] [SWABCDEF])")

    result = []
    with open(suite_file, "r") as fp:
        for line in fp:
            match = bench_pattern.search(line)
            if match:
                result.append(match.group(1))

    return result


# TODO: write tests
if __name__ == "__main__":
    npb_dir = os.getenv("NPB_DIR")
    if npb_dir is None:
        print("Set NBP_DIR environment first.")
        exit(0)
    config_dir = os.path.join(npb_dir, "config")

    result_dir = os.getenv("RESULT_DIR")
    if result_dir is None:
        print("Set RESULT_DIR environment first.")
        exit(0)

    parser = argparse.ArgumentParser(
        description="Utility script for running NPB_OMP benchmarks for various numbers "
        "of threads and cores."
    )
    parser.add_argument(
        "--suite-list",
        action="store",
        required=True,
        help="comma separated list of suite files; no blanks allowed",
    )
    parser.add_argument(
        "--threads",
        action="store",
        required=False,
        help="comma separated list of threads for each experiment; no blanks allowed",
    )
    parser.add_argument(
        "--iterations",
        action="store",
        required=False,
        help="iterations for each experiment",
    )
    parser.add_argument(
        "--compact-affinity",
        action="store_true",
        required=False,
        help="exploit hyperthreading; overridden by --full-core-run",
    )
    parser.add_argument(
        "--full-thread-run",
        action="store_true",
        required=False,
        help="run experiment using 1, 2, ..., N threads, where N is the number of logical cpus "
        "available; overridden by --full-core-run",
    )
    parser.add_argument(
        "--full-core-run",
        action="store_true",
        required=False,
        help="run experiment using 1, 2, ..., N cores, where N is the number of cores available;",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        required=False,
        help="preview npb command before run",
    )

    args, others = parser.parse_known_args()

    others = "".join(others)
    suite_list = args.suite_list.split(",")
    iterations = int(args.iterations)

    thread_list = []
    topology = SystemTopology()

    if (
        args.full_core_run
    ):  # Test scalability with only one thread per physical core
        thread_list = [1] + [
            x for x in range(1, topology.core_num + 1) if x % 2 == 0
        ]
    elif (
        args.full_thread_run
    ):  # Test scalability with one thread per logical processing unit (PU)
        thread_list = [1] + [
            x for x in range(1, topology.cpu_num + 1) if x % 2 == 0
        ]
    elif args.threads is not None:  # Custom numbers of threads
        thread_list = args.threads.split(",")
    else:
        parser.error(
            "You must provide a comma-separated list of threads for each experiment or set --full-thread-run "
            "or --full-core-run"
        )

    command = ""
    for suite_file in suite_list:
        for thread_num in thread_list:
            # NPB OMP uses this env var for thread number
            os.environ["OMP_RUN_THREADS"] = str(thread_num)

            if (
                args.compact_affinity or args.full_thread_run
            ) and not args.full_core_run:
                affinity = "compact"
            else:
                affinity = "scatter"

            if not args.preview:
                topology.switch_cpus(
                    int(thread_num), affinity, "0"
                )  # Switch off desired cpus

            os.chdir(config_dir)
            name_class_list = parse_suite(suite_file)
            for name_class in name_class_list:
                bench_name, bench_class = name_class.split()

                os.chdir(npb_dir)
                make_command = "make {} CLASS={}".format(
                    bench_name, bench_class
                )

                print(make_command)
                if not args.preview:
                    os.system(make_command)

                for iteration in range(iterations):
                    run_command_fmt = (
                        "./bin/{0}.{1}.x > {2}/{0}.{1}_out.{3}.{4}.{5}"
                    )
                    run_command = run_command_fmt.format(
                        bench_name,
                        bench_class,
                        result_dir,
                        thread_num,
                        affinity,
                        iteration + 1,
                    )
                    print(run_command)
                    if not args.preview:
                        os.system(run_command)

            topology.switch_cpus(
                int(thread_num), affinity, "1"
            )  # Switch back on desired cpus
