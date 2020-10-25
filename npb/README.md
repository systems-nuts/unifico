## Structure

* **config/**: Keeps the configuration files used for NPB runs (as *make.def* and *suite.def*)
* **results/**: Keeps the txt files from NPB runs' output

## Utility scripts

* **run_npb.py**: Compile and run NPB binaries to give lists of config files, thread number and activating/deactivating cpus on demand
* **plot_overhead.py**: Used to output a boxplot from multiplte SPEC output csvs

### Compile and run a reportable benchmark suite (equals one experiment)

```
make <benchmark> CLASS=<class> [VERSION=opt]
./bin/bt.A.x > BT.A_out.4
```

