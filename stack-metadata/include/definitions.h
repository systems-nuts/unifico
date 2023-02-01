/**
 * Definitions needed by most files.
 *
 * Author: Rob Lyerly <rlyerly@vt.edu>
 * Date: 1/6/2016
 */

#ifndef _DEFINITIONS_H
#define _DEFINITIONS_H

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "arch.h"
#include "retval.h"

/* We're using stackmap-based live values */
#define _LIVE_VALS 1

/* Generic string buffer size. */
#define BUF_SIZE 512

/* Be noisy? */
extern bool verbose;

#endif /* _DEFINITIONS_H */
