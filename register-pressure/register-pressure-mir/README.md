# Register Pressure Experiments

## Motivation
Check how many general purpose registers (GPRs) and floating-point registers (FRs) 
do we use before and after unifico.

## Requirement
MIR files of the npb benchmark.

## How To Run
```bash
./npb_reg_pressure.sh your_directory_name
# e.g. ./npb_reg_pressure.sh arm_npb_init/
```
