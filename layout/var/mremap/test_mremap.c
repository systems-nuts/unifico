#define _GNU_SOURCE
#include <stdio.h>
#include <sys/mman.h>

#define int_size(A) (A * sizeof(int))

int main()
{
    int N = 4096;
    void *old_addr = (void *)0x8ffff0000;
    int *ptr = mmap(old_addr, int_size(N), PROT_READ | PROT_WRITE,
                    MAP_PRIVATE | MAP_ANONYMOUS, 0, 0);

    if (ptr == MAP_FAILED) {
        printf("Mapping Failed\n");
        return 1;
    }
    printf("ptr is : %p \n", ptr);

    for (int i = 0; i < N; i++)
        ptr[i] = i;

    for (int i = 0; i < N; i += 512)
        printf("[%d] ", ptr[i]);
    printf("\n");

    void *new_addr = (void *)(old_addr - 0x000000001000);

    printf("old %p-%p new %p-%p\n", old_addr, (old_addr + int_size(N)),
           new_addr, (new_addr + int_size(N)));

    // sleep (100);

    //	ptr = mremap(old_addr, N * sizeof(int), N * sizeof(int),
    // MREMAP_MAYMOVE); // This works 	 ptr = mremap(old_addr, 0, N *
    // sizeof(int), MREMAP_MAYMOVE | MREMAP_FIXED, new_addr); This doesn't work
    // ptr = mremap(old_addr, int_size(N), int_size(N), MREMAP_MAYMOVE |
    // MREMAP_FIXED, new_addr);	 // in the Linux kernel code it is explictly
    // written that the old and new location SHOULD NOT overlap
    //    ptr =mremap(old_addr, int_size(N), int_size(1024*3),0 ); //<<< THIS
    //    WORKS
    //      ptr =mremap(old_addr, int_size(N), int_size(1024*5),0); // <<< THIS
    //      WORKS
    ptr = mremap(old_addr, int_size(N), int_size(1024 * 5), 0, new_addr);

    if (ptr == MAP_FAILED) {
        perror("NIKOSmremap: mremap failedNIKOS");
        return 1;
    }
    printf("ptr is : %p \n", ptr);

    // sleep (100);

    //	for(int i=0; i<N; i++)
    //		ptr[i] = 2 * i;

    for (int i = 0; i < N; i += 512)
        printf("[%d]\n ", ptr[i]);

    int err = munmap(ptr, N * sizeof(int));
    if (err != 0) {
        printf("UnMapping Failed\n");
        return 1;
    }

    return 0;
}
