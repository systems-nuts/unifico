#pragma once

#ifdef UNASL_MIGRATION

#include <signal.h>

/* a POSIX alternative for raise() is kill(pid, signal) */

#define migrate()   \
  do {              \
    raise(SIGSTOP); \
  } while (0);

#else

#define migrate() \
  do {            \
  } while (0);

#endif /* UNASL_MIGRATION */
