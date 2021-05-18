# How stack is allocated

4 Registers = 8 words
25 int of a = 25 words
Total = 33 words
But, stack must be quad-word aligned -> 36 words -> 144 bytes

# Bugs

* No random for AArch64
