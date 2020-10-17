import argparse

from .lstopo import digest_lstopo


def switch_hyperthreading(option):
    """
    Simple python wrapper for Simultaneous Multithreading (SMT) control.
    See: https://serverfault.com/questions/235825/disable-hyperthreading-from-within-linux-no-access-to-bios
    Requires sudo.
    :param option: 'on', 'off' or 'forceoff'
    :return:
    """
    if option in ['on', 'off', 'forceoff']:
        with open('/sys/devices/system/cpu/smt/control', 'w') as fp:
            fp.write(option)
    else:
        print('Unknown option.')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Utility script for running SPEC2017 benchmarks for various numbers '
                                                 'of threads and cores.')
    parser.add_argument('--config-list', action="store", required=True,
                        help='comma separated list of config files; no blanks allowed')
    parser.add_argument('--threads', action="store", required=False,
                        help='comma separated list of threads for each experiment; no blanks allowed')
    parser.add_argument('--cores-only', action="store_true", required=False,
                        help='disable hyperthreading')
    parser.add_argument('--full-thread-run', action="store_true", required=False,
                        help='run experiment using 1, 2, ..., N threads, where N is the number of logical cpus '
                             'available; overridden by --full-core-run')
    parser.add_argument('--full-core-run', action="store_true", required=False,
                        help='run experiment using 1, 2, ..., N cores, where N is the number of cores available; '
                             'overrides --full-thread-run')
    parser.add_argument('--lstopo-output', action="store", required=False,
                        help='output of \'lstopo-no-graphics -p\' for this machine')

    args, others = parser.parse_known_args()

    config_list = args.config_list.split(',')

    if (args.full_thread_run or args.cores_only) and args.lstopo_output is None:
        parser.error('Output of \'lstopo-no-graphics -p\' required when --full-thread-run or --full-core-run are set.')

    thread_list = []
    if args.full_core_run:  # Test scalability with only one thread per physical core
        pu_details = digest_lstopo(args.lstopo_output)
        core_ids = set([core_id for (_, core_id, _) in pu_details])
        core_num = len(core_ids)
        thread_list = [1] + [x for x in range(1, core_num + 1) if x % 2 == 0]
    elif args.full_thread_run:  # Test scalability with one thread per logical processing unit (PU)
        pu_num = len(digest_lstopo(args.lstopo_output))
        thread_list = [1] + [x for x in range(1, pu_num + 1) if x % 2 == 0]
    elif args.threads is not None:  # Custom numbers of threads
        thread_list = args.threads.split(',')
    else:
        parser.error('You must provide a comma-separated list of threads for each experiment or set --full-thread-run '
                     'or --full-core-run')

    if args.cores_only or args.full_core_run:
        switch_hyperthreading('off')
    print(thread_list)

    command = ''
    for config_file in config_list:
        for thread_num in thread_list:
            command = 'runcpu -c {} --reportable --threads {} -o csv intspeed'.format(config_file, thread_num)
            print(command)
        # os.system(command)

    if args.cores_only or args.full_core_run:
        switch_hyperthreading('on')
