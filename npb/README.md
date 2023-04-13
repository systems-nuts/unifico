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
* Run: `sudo -E bash -c "python3.7 -m unified_abi.npb.run_npb --suite-list suite.def \ 
        --threads=12 --compact-affinity --iterations=1"`
* Optionally: add the flag `--preview` to see the commands to be executed

### Fetch results from nettuno

* `ssh nikos@129.215.165.71`
* `scp -r nikos@nettuno:phd/unified_abi/npb/results .`
* `exit`
* `cd /dest/of/results`
* `scp nikos@129.215.165.71:results/* .`


---------------------------------------------

## Steps to run NPB Benchmark for Asplos
### prepare json of `run_bmks`
```bash
# copy the json template and modify it.
cp runs/configs/main_example.json .
vi main_example.json
# replace `executables` to the one or ones you want to run
# replace `bindir` to the directory with binary exes
# replace `iterations` to the iterations you want. for the paper of asplos, we use 5.
```

### extract all bins to a standalone directory
```bash
# in the example, we extract them to ~/bins
./collect_bins.sh ../layout/npb/ ~/bins
```

### run benchmark
```bash
runs/run_bmks.py -c main_example.json
# results dir is ./run_exec_time_xxx
```

### prepare data and plot figure
```bash
# calculate speed-up manually
# copy the geomean result to the csv file
vi data/asplos2023/asplos2023_arm_speedup.csv

# plot figure
plots/plot_barchart.py -f data/asplos2023/asplos2023_arm_speedup.csv -s default -c plots/configs/speedup/barchart_arm.json
```

