## Register Loads/Stores Profiling Tool

### Usage

* Requires the installation of Intel's Pin.

```bash 
make PIN_ROOT=<pin_installation_dir> obj-intel64/register_loads_stores.so
<pin_executable_location> -t obj-intel64/register_loads_stores.so -o <out-file-name> [-f <function-name>] -- <application> [<arguments>]
```
