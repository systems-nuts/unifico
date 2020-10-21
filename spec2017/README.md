## Structure

* **config/**: Keeps the configuration files used for SPEC runs
* **results/**: Keeps the csv files from SPEC runs output

## Utility scripts

* **run_spec.py**: Wrapper over *runcpu* command of SPEC to give lists of config files, thread number and activating/deactivating cpus on demand
* **plot_overhead.py**: Used to output a boxplot from multiplte SPEC output csvs

### To run a reportable benchmark suite (equals one experiment)

```
runcpu -c=my_config_file --reportable -o csv intspeed
```

