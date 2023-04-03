/* main.c */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/shm.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

int main(void)
{
    size_t size_of_mem = 1024;
    int fd =
        shm_open("/myregion", O_CREAT | O_RDWR, S_IRWXO | S_IRUSR | S_IWUSR);
    if (fd == -1) {
        perror("Error in shm_open");
        return EXIT_FAILURE;
    }

    if (ftruncate(fd, size_of_mem) == -1) {
        perror("Error in ftruncate");
        return EXIT_FAILURE;
    }

    void *shm_address = mmap(0, size_of_mem, PROT_READ | PROT_WRITE | PROT_EXEC,
                             MAP_SHARED, fd, 0);
    if (shm_address == MAP_FAILED) {
        perror("Error mmapping the file");
        return EXIT_FAILURE;
    }

    /* Increase shard memory */
    for (size_t i = 0; i < 1024; ++i) {

        /* Does 8 align memory page? */
        size_t new_size_of_mem = 1024 + (8 * i);

        if (ftruncate(fd, new_size_of_mem) == -1) {
            perror("Error in ftruncate");
            return EXIT_FAILURE;
        }

        /*
         *            mremap() works with  aligned memory pages.
         *                       How to properly increase shared memory in this
         * case?
         *                               */
        void *temp =
            mremap(shm_address, size_of_mem, new_size_of_mem, MREMAP_MAYMOVE);
        if (temp == (void *)-1) {
            perror("Error on mremap()");
            return EXIT_FAILURE;
        }

        shm_address = temp;

        size_of_mem = new_size_of_mem;
    }

    return 0;
}
