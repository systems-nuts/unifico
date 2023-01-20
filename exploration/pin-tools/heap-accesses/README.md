## Heap Access Profiling Tool

### Usage

* Requires the installation of Intel's Pin.

```bash 
make PIN_ROOT=<pin_installation_dir> obj-intel64/HeapAccesses.so
<pin_executable_location> -t obj-intel64/HeapAccesses.so -- <application> <arguments>
```