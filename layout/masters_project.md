Simplifying heterogeneous migration between x86 and ARM machines

Heterogeneous computing is the strategy of deploying multiple types of processing elements within a single workflow, and allowing each to perform the tasks to which it is best suited.
Heterogeneity involves heterogeneous CPUs, like ARM and x86, heterogeneous processing units, like general purpose (x86) and special purpose units (GPUs, TPUs, accelerators), and also reconfigurable integrated circuits, like FPGAs.
The project will focus on the x86/ARM configuration.
Current approaches require the transformation at runtime of the stack from one architecture to another, in order to migrate a thread.
We aim to simplify the migration process, by examining the effect of a common stack layout between the x86 and ARM binaries.
Progress has been made on keeping a similar stack when only General Purpose Registers are used.
A goal of this project would be to extend current work to support floating-point registers or vector extensions that a processor may provide.
Also, the development of automated tools for the examination and comparison of the two stacks, would be of importance.
Lastly, the performance and energy-efficiency of the above effort compared to current approaches will be benchmarked.