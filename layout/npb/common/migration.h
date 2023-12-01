#pragma once

// #define UNASL_MIGRATION_TIMERS 1

#ifdef UNASL_MIGRATION

#include <signal.h>

/* a POSIX alternative for raise() is kill(pid, signal) */

#define migrate()                                                              \
    do {                                                                       \
        raise(SIGSTOP);                                                        \
    } while (0);

#else

#define migrate()                                                              \
    do {                                                                       \
    } while (0);

#endif /* UNASL_MIGRATION */

#ifdef UNASL_MIGRATION_TIMERS

#include <stdio.h>
#include <sys/time.h>

#define _UNASL_TIMER_NUM 4
#define UNASL_TIMERS_DECLARE                                                   \
    extern double unasl_timers[_UNASL_TIMER_NUM];                              \
    extern int unasl_current_timer;

#define UNASL_TIMERS_INIT                                                      \
    double unasl_timers[_UNASL_TIMER_NUM] = {0};                               \
    int unasl_current_timer = -1;

#define unasl_timers_snapshot()                                                \
    do {                                                                       \
        struct timeval tv;                                                     \
        gettimeofday(&tv, (void *)0);                                          \
        unasl_timers[++unasl_current_timer] = tv.tv_sec + 1.0e-6 * tv.tv_usec; \
    } while (0)

#define unasl_timers_print()                                                   \
    do {                                                                       \
        for (int i = 1; i < _UNASL_TIMER_NUM; ++i) {                           \
            printf("unasl time (in secs) for part %d %9.3f\n", i - 1,          \
                   unasl_timers[i] - unasl_timers[i - 1]);                     \
        }                                                                      \
    } while (0)

#else

#define UNASL_TIMERS_DECLARE ;
#define UNASL_TIMERS_INIT ;

#define unasl_timers_snapshot()                                                \
    do {                                                                       \
    } while (0);

#define unasl_timers_print()                                                   \
    do {                                                                       \
    } while (0);

#endif /* UNASL_MIGRATION_TIMERS */
