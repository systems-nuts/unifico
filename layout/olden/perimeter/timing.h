/*
 * Common harness timing routines
 */

#include "config.h"

#ifdef HAVE_UNISTD_H

#if __STDC_VERSION__ >= 199901L
#define _XOPEN_SOURCE 600
#else
#define _XOPEN_SOURCE 500
#endif /* __STDC_VERSION__ */

#include <time.h>
#include <unistd.h>
#endif /* HAVE_UNISTD_H */

#if defined(HAVE_UNISTD_H) && (_POSIX_TIMERS > 0) &&                           \
    defined(_POSIX_MONOTONIC_CLOCK)
#define OLDEN_TIME(x) clock_gettime(CLOCK_MONOTONIC_RAW, &x)
#define OLDEN_DURATION_MS(start, stop)                                         \
    ((double)stop.tv_sec - start.tv_sec) * 1000 +                              \
        (double)(stop.tv_nsec - start.tv_nsec) / 1000000
#else
#define OLDEN_TIME(x)                                                          \
    do {                                                                       \
    } while (0)
#define OLDEN_DURATION_MS(start, stop) 0.0
#endif
