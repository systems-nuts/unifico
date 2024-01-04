# Unifico Artifact Evaluation

## Get docker image

```bash
docker pull unificocc24/unifico
docker run -it unifico
cd /code/unifico-cc24
source venv/bin/activate
pip install -r requirements.txt
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
```

* Class `S` is for testing.
* For the experiments use one of `A, B, C`, as shown in the paper.


### Get the binary sizes from the binaries

```bash
cd /code/unifico-cc24/npb/runs/experiments/performance-regression

mkdir -p ../../../../plots/binaries-sections-size-comparison/B/o1/unifico/x86/
for npb in bt cg ep ft is lu mg sp ua; do
  cp o1/unifico/nettuno/bin/${npb}_x86_64_aligned.out_S_size.log ../../../../plots/binaries-sections-size-comparison/B/o1/unifico/x86/${npb}.txt
done

mkdir -p ../../../../plots/binaries-sections-size-comparison/B/o1/unifico/arm/
for npb in bt cg ep ft is lu mg sp ua; do
  cp o1/unifico/sole/bin/${npb}_aarch64_aligned.out_B_size.log ../../../../plots/binaries-sections-size-comparison/B/o1/unifico/arm/${npb}.txt
done

mkdir -p ../../../../plots/binaries-sections-size-comparison/B/o1/vanilla/x86
for npb in bt cg ep ft is lu mg sp ua; do
  cp o1/vanilla/nettuno/bin/${npb}_x86_64_init.out_B_size.log ../../../../plots/binaries-sections-size-comparison/B/o1/vanilla/x86/${npb}.txt
done

mkdir -p ../../../../plots/binaries-sections-size-comparison/B/o1/vanilla/arm/
for npb in bt cg ep ft is lu mg sp ua; do
    cp o1/vanilla/sole/bin/${npb}_aarch64_init.out_B_size.log ../../../../plots/binaries-sections-size-comparison/B/o1/vanilla/arm/${npb}.txt
done
```

## Plot the results

```bash
cd /code/unifico/npb

# Plot binary sizes
for arch in arm x86; do
    plots/plot_barchart.py -f data/cc2024/binary_sizes_o1_B_${arch}.csv -s plots/configs/binary_sizes/stacked_barchart.mplstyle -c plots/configs/binary_sizes/stacked_barchart_${arch}.json
done

# Plot overheads
for arch in arm x86; do
    plots/plot_barchart.py -f data/cc2024/${arch}_overhead.csv -s plots/configs/overhead/barchart_${arch}.mplstyle -c plots/configs/overhead/barchart_${arch}.json
done
```