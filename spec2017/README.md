## Utility scripts

* **lstopo.py**: Used to process the output of lstopo-no-graphics
* **run_spec.py**: Wrapper over *runcpu* command of SPEC to give lists of config files, thread number and activating/deactivating cpus on demand

### To run a reportable benchmark suite (equals one experiment)

```
runcpu -c=my_config_file --reportable -o csv intspeed
```

