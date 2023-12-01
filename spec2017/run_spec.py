import argparse
import os

from utilities.system_topology import SystemTopology

# TODO: write tests
if __name__ == "__main__":
    spec_dir = os.getenv("SPEC_DIR")
    if spec_dir is None:
        print(
            "Set SPEC_DIR environment first (usually source a script inside SPEC dir)."
        )
        exit(0)

    parser = argparse.ArgumentParser(
        description="Utility script for running SPEC2017 benchmarks for various numbers "
        "of threads and cores."
    )
    parser.add_argument(
        "--config-list",
        action="store",
        required=True,
        help="comma separated list of config files; no blanks allowed",
    )
    parser.add_argument(
        "--threads",
        action="store",
        required=False,
        help="comma separated list of threads for each experiment; no blanks allowed",
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
        "--bench",
        action="store",
        required=False,
        help="benchmark or group of benchmarks to run",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        required=False,
        help="preview spec command before run",
    )

    args, others = parser.parse_known_args()

    others = " ".join(others)
    config_list = args.config_list.split(",")

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
        thread_list = [int(t) for t in thread_list]
    else:
        parser.error(
            "You must provide a comma-separated list of threads for each experiment or set --full-thread-run "
            "or --full-core-run"
        )

    if args.bench is None:
        bench = "intspeed"
    else:
        bench = args.bench.split(",")
        bench = " ".join(bench)

    build_command = ""
    run_command = ""
    for config_file in config_list:
        for thread_num in thread_list:
            if (
                args.compact_affinity or args.full_thread_run
            ) and not args.full_core_run:
                affinity = "compact"
            else:
                affinity = "scatter"

            build_command_fmt = "{}/bin/runcpu -c {} -a build -o csv {} {}"
            build_command = build_command_fmt.format(
                spec_dir, config_file, bench, others
            )

            run_command_fmt = "{}/bin/runcpu -c {} --threads {} -o csv {} {}"
            run_command = run_command_fmt.format(
                spec_dir, config_file, thread_num, bench, others
            )

            print(build_command)
            if not args.preview:
                os.system(build_command)
                topology.switch_cpus(
                    int(thread_num), affinity, "0"
                )  # Switch off desired cpus

            print(run_command)
            if not args.preview:
                os.system(
                    run_command
                )  # Run benchmarks for the specific config file and the specific number of threads

            if not args.preview:
                topology.switch_cpus(
                    int(thread_num), affinity, "1"
                )  # Switch back on desired cpus
