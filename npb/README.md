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
