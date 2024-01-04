# Unifico Artifact Evaluation

## Get the docker image

```bash
docker pull unificocc24/unifico
docker run -it unifico
```

## Build and run experiments

* Note that both x86 and arm binaries are build on X86.
* In order to run the arm binaries, these need to be copied to an arm machine.
* For this, modify the following configs with the necessary `ssh` command:
* `npb/runs/configs/performance-regression/o1/unifico/sole/build_run_arm.json`
* `npb/runs/configs/performance-regression/o1/vanilla/sole/build_run_arm.json`
* Then, you can the following commands (for execution only on x86, `perf_x86.sh` is sufficient).


```bash
cd /code/unifico/npb/runs/

# Build the unifico and vanilla arm binaries for class S (on the x86 machine)
./scripts/build_arm.sh unifico vanilla S 

# Build and run the unifico and vanilla x86 binaries for class S (on the x86 machine)
./scripts/perf_x86.sh unifico vanilla S

# Run the unifico and vanilla arm binaries for class S (on the arm machine)
./scripts/perf_x86.sh unifico vanilla S

# Merge csvs for all classes (remove a class from {A,B,C} depending on what was run)
python ./plots/merge_csv.py data/cc2024/x86_overhead.csv runs/experiments/performance-regression/o1/vanilla/sole/overhead_{A,B,C}.csv
python ./plots/merge_csv.py data/cc2024/arm_overhead.csv runs/experiments/performance-regression/o1/vanilla/sole/overhead_{A,B,C}.csv
```

* Class `S` is for testing.
* For the experiments use one of `A, B, C`, as shown in the paper.


### Get the binary sizes from the binaries

* Build the binaries for the class B (as in the paper).

```bash
cd /code/unifico-cc24/npb/runs
source ../../venv/bin/activate

# Build vanilla binaries
python npb_run.py \
  --config configs/performance-regression/o1/vanilla/nettuno/build_run_x86.json \
  --dest experiments/performance-regression/o1/vanilla/nettuno \
  --npb-class B \
  --build
  
# Build unifico binaries
python npb_run.py \
  --config configs/performance-regression/o1/unifico/nettuno/build_run_x86.json \
  --dest experiments/performance-regression/o1/unifico/nettuno \
  --npb-class B \
  --build
```

* Aggregate the results in one csv.

```bash
cd /code/unifico-cc24/npb/runs/experiments/performance-regression

# x86 machine

mkdir -p ../../../../plots/binaries-sections-size-comparison/B/o1/unifico/x86/
for npb in bt cg ep ft is lu mg sp ua; do
  cp o1/unifico/nettuno/bin/${npb}_x86_64_aligned.out_B_size.log ../../../../plots/binaries-sections-size-comparison/B/o1/unifico/x86/${npb}.txt
done

mkdir -p ../../../../plots/binaries-sections-size-comparison/B/o1/vanilla/x86
for npb in bt cg ep ft is lu mg sp ua; do
  cp o1/vanilla/nettuno/bin/${npb}_x86_64_init.out_B_size.log ../../../../plots/binaries-sections-size-comparison/B/o1/vanilla/x86/${npb}.txt
done

cd /code/unifico-cc24/plots/binaries-sections-size-comparison

# arm machine

mkdir -p ../../../../plots/binaries-sections-size-comparison/B/o1/unifico/arm/
for npb in bt cg ep ft is lu mg sp ua; do
  cp o1/unifico/sole/bin/${npb}_aarch64_aligned.out_B_size.log ../../../../plots/binaries-sections-size-comparison/B/o1/unifico/arm/${npb}.txt
done

mkdir -p ../../../../plots/binaries-sections-size-comparison/B/o1/vanilla/arm/
for npb in bt cg ep ft is lu mg sp ua; do
    cp o1/vanilla/sole/bin/${npb}_aarch64_init.out_B_size.log ../../../../plots/binaries-sections-size-comparison/B/o1/vanilla/arm/${npb}.txt
done
```

## Plot the results

```bash
cd /code/unifico-cc24/npb
source ../venv/bin/activate

# Plot binary sizes
# x86
plots/plot_barchart.py -f data/cc2024/binary_sizes_o1_B_x86.csv -s plots/configs/binary_sizes/stacked_barchart.mplstyle -c plots/configs/binary_sizes/stacked_barchart_x86.json
# arm
plots/plot_barchart.py -f data/cc2024/binary_sizes_o1_B_arm.csv -s plots/configs/binary_sizes/stacked_barchart.mplstyle -c plots/configs/binary_sizes/stacked_barchart_arm.json

# Plot overheads
# x86
plots/plot_barchart.py -f data/cc2024/x86_overhead.csv -s plots/configs/overhead/barchart_x86.mplstyle -c plots/configs/overhead/barchart_x86.json
# arm
plots/plot_barchart.py -f data/cc2024/arm_overhead.csv -s plots/configs/overhead/barchart_arm.mplstyle -c plots/configs/overhead/barchart_arm.json
```