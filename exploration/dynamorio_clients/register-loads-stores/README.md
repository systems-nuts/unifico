## Register Loads/Stores Profiling Tool

### Usage

* Requires the installation of DynamoRIO.

```bash 
mkdir build
cd build
cmake -DDynamoRIO_DIR=$DYNAMORIO_HOME/cmake ..
make
cd ..
$DYNAMORIO_HOME/bin64/drrun -c build/libregister_loads_stores.so <-only_from_app> -- /bin/ls
```

* The `only_from_app` code ignores the library code (TODO: check).
