# Running experiments

### Export the top-level NPB directory

```bash
export NPB_PATH=<path_to_npb>
```

### Test

```bash
# 1. on the x86 machine
./scripts/test_x86.sh <experiment>

# 2. on the arm machine
./scripts/test_arm.sh <experiment>
```

### Performance regression

* Once the step 1. is done, the steps 2. and 3. can be run independently.

```bash
# 1. Build the arm binaries on the x86 machine
./scripts/build_arm.sh <experiment> <baseline> <npb_class>

# 2. Run the experiment on the x86 machine
# might require sudo for setting the scaling governor
./scripts/perf_x86.sh  <experiment> <baseline> <npb_class>

# 3. Run the experiment on the arm machine
./scripts/perf_arm.sh  <experiment> <baseline> <npb_class>
```