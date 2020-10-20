import argparse
import shutil
import os


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Utility script for running PARSEC benchmarks for various numbers '
                                                 'of threads and cores.')
    parser.add_argument('--config-list', action="store", required=True,
                        help='comma separated list of config files; no blanks allowed')
    parser.add_argument('--input', action="store", required=True,
                        help='parsec input type')

    args, others = parser.parse_known_args()

    config_list = args.config_list.split(',')

    os.chdir('/home/blackgeorge/Documents/phd/benchmarks/parsec-3.0')

    for config_file in config_list:
        for bench_group in ['apps', 'kernels']:
            for bench in os.listdir('pkgs/{}'.format(bench_group)):
                print('config/{}'.format(config_file), 'pkgs/{}/{}/parsec'.format(bench_group, bench))
                shutil.copy('config/{}'.format(config_file), 'pkgs/{}/{}/parsec'.format(bench_group, bench))

            build_cmd = 'parsecmgmt -a build -p {} -c {}'.format(bench_group, config_file)
            os.system(build_cmd)
            print(build_cmd)
            run_cmd = 'parsecmgmt -a run -p {} -c {} -i {}'.format(bench_group, config_file, args.input)
            os.system(run_cmd)
            print(run_cmd)
