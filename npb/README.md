# NPB Runner Pipeline

## Installation

* Install the project in editable mode with:

```bash
cd unified_abi
pip install -e .
```

## Steps to run NPB Benchmarks

* Move to the `npb/` directory.
* Export the location of the npb build directory (`NPB_PATH`).

```bash
cd unified_abi/npb
export NPB_PATH=<path-to-npb>  # E.g., export NPB_PATH=/home/nikos/phd/unified_abi/layout/npb
```

### JSON Config

```bash
# Use one of the JSON config files in `runs/configs (or create a new one)
cp runs/configs/build_run_is_S.json runs/configs/<new-config.json>
vi runs/configs/<new-config.json>
# Replace `executables` to the one or ones you want to build/run
# If necessary, modify the `build` commands.
# If necessary, modify the `run` commands.
# Replace `iterations` with the number iterations you want (usually 3 or 5).
```

### Using the NPB Runner

#### Help

```bash
npb --help
```

#### Build the binaries

```bash
# This will create the binaries in the `bins/` folder
npb --config runs/configs/build_run_is_S.json --build
npb -c runs/configs/build_run_is_S.json -b  # Equivalent
```

#### Run the binaries

```bash
# This will run the binaries in the `bins/` folder
npb --config runs/configs/build_run_is_S.json --run
npb -c runs/configs/build_run_is_S.json -r  # Equivalent
```

#### Build and run

```bash
npb -c runs/configs/build_run_is_S.json -b -r  # Equivalent
```

### prepare data and plot figure
```bash
# calculate speed-up manually
# copy the geomean result to the csv file
vi data/asplos2023/asplos2023_arm_speedup.csv

# plot figure
plots/plot_barchart.py -f data/asplos2023/asplos2023_arm_speedup.csv -s plots/configs/speedup/barchart_arm.mplstyle -c plots/configs/speedup/barchart_arm.json
plots/plot_barchart.py -f data/asplos2023/asplos2023_x86_speedup.csv -s plots/configs/speedup/barchart_x86.mplstyle -c plots/configs/speedup/barchart_x86.json
```

---------------------------------------------

## Structure

* **config/**: Keeps the configuration files used for NPB runs (as *make.def* and *suite.def*)
* **results/**: Keeps the txt files from NPB runs' output

## Utility scripts

* **run_npb.py**: Compile and run NPB binaries to give lists of config files, thread number and activating/deactivating cpus on demand.

    Set the `NPB_DIR` with the path of the NPB directory and `NPB_SCRIPT_DIR` with the main script directory containing `config/` and `results/` folders.
    Example:

      export NPB_DIR=/home/user/NPB3.4.1/NPB3.4-OMP
      export NPB_SCRIPT_DIR=/home/user/my_npb_script_dir

* **plot_overhead.py**: Used to output a boxplot from multiplte NPB output csvs

### Compile and run a reportable benchmark suite (equals one experiment)

```
make <benchmark> CLASS=<class> [VERSION=opt]
./bin/bt.A.x > BT.A_out.4
```

### Use main script to run benchmarks

* Create a make.def file in `NPB_DIR/config`
* Create a suite.def file in `NPB_SCRIPT_DIR/config`
* Run: `sudo -E bash -c "python3.7 -m unified_abi.npb.run_npb --suite-list suite.def --threads=12 --compact-affinity --iterations=1"`
* Optionally: add the flag `--preview` to see the commands to be executed

### Fetch results from nettuno

* `ssh nikos@129.215.165.71`
* `scp -r nikos@nettuno:phd/unified_abi/npb/results .`
* `exit`
* `cd /dest/of/results`
* `scp nikos@129.215.165.71:results/* .`


---------------------------------------------
