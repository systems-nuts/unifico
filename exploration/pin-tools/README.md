## Pin Tools

This folder contains out-of-tree pin tools for our experiments. It is assumed that pin has been installed. More info [here](https://software.intel.com/sites/landingpage/pintool/docs/98650/Pin/doc/html/index.html#INSTALLATION).

### Setup

To compile and run a tool, e.g., `MemoryAccesses`, run:

```bash
cd memory-accesses
make PIN_ROOT=<path-to-pin-root> obj-intel64/MemoryAccesses.so
<path-to-pin-root> -t obj-intel64/MemoryAccesses.so -- /bin/ls
```

More info [here](https://software.intel.com/sites/landingpage/pintool/docs/98650/Pin/doc/html/index.html#BUILDINGTOOLS).