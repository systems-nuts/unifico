#define _GNU_SOURCE
#include <assert.h>
#include <sched.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

#define nop ({ __asm__ volatile("nop\n\t" : : : "memory"); })
#define nop2                                                                   \
    ({                                                                         \
        nop;                                                                   \
        nop;                                                                   \
    })
#define nop4                                                                   \
    ({                                                                         \
        nop2;                                                                  \
        nop2;                                                                  \
    })
#define nop8                                                                   \
    ({                                                                         \
        nop4;                                                                  \
        nop4;                                                                  \
    })
#define nop16                                                                  \
    ({                                                                         \
        nop8;                                                                  \
        nop8;                                                                  \
    })
#define nop32                                                                  \
    ({                                                                         \
        nop16;                                                                 \
        nop16;                                                                 \
    })
#define nop64                                                                  \
    ({                                                                         \
        nop32;                                                                 \
        nop32;                                                                 \
    })
#define nop128                                                                 \
    ({                                                                         \
        nop64;                                                                 \
        nop64;                                                                 \
    })
#define nop256                                                                 \
    ({                                                                         \
        nop128;                                                                \
        nop128;                                                                \
    })
#define nop512                                                                 \
    ({                                                                         \
        nop256;                                                                \
        nop256;                                                                \
    })
#define nop1024                                                                \
    ({                                                                         \
        nop512;                                                                \
        nop512;                                                                \
    })

// static const unsigned ITERATIONS = 1000;
// static const unsigned ITERATIONS = 1000000;
static const unsigned ITERATIONS = 1000000000;

double what_time_is_it()
{
    struct timespec now;
    clock_gettime(CLOCK_REALTIME, &now);
    return now.tv_sec + now.tv_nsec * 1e-9;
}

// Code taken from
// https://stackoverflow.com/questions/10490756/how-to-use-sched-getaffinity-and-sched-setaffinity-in-linux-from-c
void print_affinity()
{
    cpu_set_t mask;
    long nproc, i;

    if (sched_getaffinity(0, sizeof(cpu_set_t), &mask) == -1) {
        perror("sched_getaffinity");
        assert(false);
    }

    nproc = sysconf(_SC_NPROCESSORS_ONLN);

    printf("sched_getaffinity = ");
    for (i = 0; i < nproc; i++) {
        printf("%d ", CPU_ISSET(i, &mask));
    }
    printf("\n");
}

int main()
{
    // FIFO scheduling
    struct sched_param sp = {.sched_priority = 90};
    sched_setscheduler(0, SCHED_FIFO, &sp);

    // Affinity setting
    cpu_set_t mask;

    printf("sched_getcpu = %d\n", sched_getcpu());

    CPU_ZERO(&mask);
    CPU_SET(0, &mask);
    if (sched_setaffinity(0, sizeof(cpu_set_t), &mask) == -1) {
        perror("sched_setaffinity");
        assert(false);
    }

    /* TODO is it guaranteed to have taken effect already? Always worked on my
     * tests. */
    printf("sched_getcpu = %d\n", sched_getcpu());

    printf("Time in micro seconds:\n");

    double t0 = what_time_is_it();
    for (int i = 0; i < ITERATIONS; ++i)
        nop;
    printf("nop,%.6lf\n", what_time_is_it() - t0);

    t0 = what_time_is_it();
    for (int i = 0; i < ITERATIONS; ++i)
        nop2;
    printf("nop2,%.6lf\n", what_time_is_it() - t0);

    t0 = what_time_is_it();
    for (int i = 0; i < ITERATIONS; ++i)
        nop4;
    printf("nop4,%.6lf\n", what_time_is_it() - t0);

    t0 = what_time_is_it();
    for (int i = 0; i < ITERATIONS; ++i)
        nop8;
    printf("nop8,%.6lf\n", what_time_is_it() - t0);

    t0 = what_time_is_it();
    for (int i = 0; i < ITERATIONS; ++i)
        nop16;
    printf("nop16,%.6lf\n", what_time_is_it() - t0);

    t0 = what_time_is_it();
    for (int i = 0; i < ITERATIONS; ++i)
        nop32;
    printf("nop32,%.6lf\n", what_time_is_it() - t0);

    t0 = what_time_is_it();
    for (int i = 0; i < ITERATIONS; ++i)
        nop64;
    printf("nop64,%.6lf\n", what_time_is_it() - t0);

    t0 = what_time_is_it();
    for (int i = 0; i < ITERATIONS; ++i)
        nop128;
    printf("nop128,%.6lf\n", what_time_is_it() - t0);

    t0 = what_time_is_it();
    for (int i = 0; i < ITERATIONS; ++i)
        nop256;
    printf("nop256,%.6lf\n", what_time_is_it() - t0);

    t0 = what_time_is_it();
    for (int i = 0; i < ITERATIONS; ++i)
        nop512;
    printf("nop512,%.6lf\n", what_time_is_it() - t0);

    t0 = what_time_is_it();
    for (int i = 0; i < ITERATIONS; ++i)
        nop1024;
    printf("nop1024,%.6lf\n", what_time_is_it() - t0);

    return 0;
}
