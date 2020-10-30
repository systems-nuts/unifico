#include <inttypes.h>

uint64_t inc(uint64_t i) {
	__asm__ __volatile__(
			""
			: "+m" (i)
			:
			: "r14"
			);
    return i + 1;
}

int main(int argc, char **argv) {
    (void)argv;
    return inc(argc);
}
