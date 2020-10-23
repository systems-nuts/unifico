import argparse
import os

from unified_abi.utilities.lstopo import digest_lstopo
from unified_abi.utilities.switch_cpu import switch_cpu


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Utility script for running SPEC2017 benchmarks for various numbers '
                                                 'of threads and cores.')
    parser.add_argument('--config-list', action="store", required=True,
                        help='comma separated list of config files; no blanks allowed')
    parser.add_argument('--threads', action="store", required=False,
                        help='comma separated list of threads for each experiment; no blanks allowed')
    parser.add_argument('--compact-affinity', action="store_true", required=False,
                        help='exploit hyperthreading')
    parser.add_argument('--full-thread-run', action="store_true", required=False,
                        help='run experiment using 1, 2, ..., N threads, where N is the number of logical cpus '
                             'available; overridden by --full-core-run')
    parser.add_argument('--full-core-run', action="store_true", required=False,
                        help='run experiment using 1, 2, ..., N cores, where N is the number of cores available; '
                             'overrides --full-thread-run')
    parser.add_argument('--lstopo-output', action="store", required=True,
                        help='output of \'lstopo-no-graphics -p\' for this machine')
    parser.add_argument('--bench', action="store", required=False,
                        help='benchmark or group of benchmarks to run')
    parser.add_argument('--preview', action="store_true", required=False,
                        help='preview spec command before run')
    parser.add_argument('--reset_cpus', action="store_true", required=False,
                        help='reset cpus')

    args, others = parser.parse_known_args()

    config_list = args.config_list.split(',')

    thread_list = []
    topology_details = digest_lstopo(args.lstopo_output)

    compact_list = []
    core_num = 0
    for package in topology_details['packages']:
        for core in package['cores']:
            compact_list.extend(core['cpus'])
            core_num += len(core['cpus'])

    cpu_num = len(compact_list)
    scatter_list = list(range(0, cpu_num))

    if args.full_core_run:  # Test scalability with only one thread per physical core
        thread_list = [1] + [x for x in range(1, core_num + 1) if x % 2 == 0]
    elif args.full_thread_run:  # Test scalability with one thread per logical processing unit (PU)
        thread_list = [1] + [x for x in range(1, cpu_num + 1) if x % 2 == 0]
    elif args.threads is not None:  # Custom numbers of threads
        thread_list = args.threads.split(',')
        thread_list = [int(t) for t in  thread_list]
    else:
        parser.error('You must provide a comma-separated list of threads for each experiment or set --full-thread-run '
                     'or --full-core-run')

    if args.bench is None:
        bench = 'intspeed'
    else:
        bench = args.bench

    command = ''
    for config_file in config_list:
        for thread_num in thread_list:

            # TODO: Take dir from env variable
            command_fmt = '/home/nikos/cpu2017/bin/runcpu -c {} --reportable --threads {} -o csv {}'
            command = command_fmt.format(config_file, thread_num, bench)

            cpus_to_reset = list(range(1, cpu_num))  # We usually can't mess with cpu0 anyway

            if args.reset_cpus:  # TODO: remove
                switch_cpu(cpus_to_reset, '1')  # Make sure all cpus are active before the program begins

            if args.preview:
                print(command)
                exit(0)

            # switch_cpu(cpus_to_reset, '1')  # Make sure all cpus are active before the program begins

            if args.compact_affinity:
                cpus_to_deactivate = compact_list[thread_num:]
            else:
                cpus_to_deactivate = scatter_list[thread_num:]

            print('Deactivating cpus: ', cpus_to_deactivate)
            try:
                switch_cpu(cpus_to_deactivate, '0')  # Deactivate rest of the cpus
            except Exception as e:
                switch_cpu(cpus_to_deactivate, '1')  # Reactivate

            os.system(command)  # Run benchmarks for the specific config file and the specific number of threads
            switch_cpu(cpus_to_deactivate, '1')  # Reactivate
