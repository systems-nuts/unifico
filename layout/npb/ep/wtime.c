#include "wtime.h"
#ifndef UNASL_MIGRATION
#include <time.h>
#ifndef DOS
#include <sys/time.h>
#endif
#endif /* UNASL_MIGRATION */

void wtime(double *t)
{
#ifdef UNASL_MIGRATION
    *t = 0;
#else
    static int sec = -1;
    struct timeval tv;
    gettimeofday(&tv, (void *)0);
    if (sec < 0)
        sec = tv.tv_sec;
    *t = (tv.tv_sec - sec) + 1.0e-6 * tv.tv_usec;
#endif /* UNASL_MIGRATION */
}
