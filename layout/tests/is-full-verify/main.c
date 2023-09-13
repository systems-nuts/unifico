#include "npbparams.h"
#include <stdio.h>

#define USE_BUCKETS

/******************/
/* default values */
/******************/
#ifndef CLASS
#define CLASS 'S'
#endif

/*************/
/*  CLASS S  */
/*************/
#if CLASS == 'S'
#define TOTAL_KEYS_LOG_2 16
#define MAX_KEY_LOG_2 11
#define NUM_BUCKETS_LOG_2 9
#endif

/*************/
/*  CLASS W  */
/*************/
#if CLASS == 'W'
#define TOTAL_KEYS_LOG_2 20
#define MAX_KEY_LOG_2 16
#define NUM_BUCKETS_LOG_2 10
#endif

/*************/
/*  CLASS A  */
/*************/
#if CLASS == 'A'
#define TOTAL_KEYS_LOG_2 23
#define MAX_KEY_LOG_2 19
#define NUM_BUCKETS_LOG_2 10
#endif

/*************/
/*  CLASS B  */
/*************/
#if CLASS == 'B'
#define TOTAL_KEYS_LOG_2 25
#define MAX_KEY_LOG_2 21
#define NUM_BUCKETS_LOG_2 10
#endif

/*************/
/*  CLASS C  */
/*************/
#if CLASS == 'C'
#define TOTAL_KEYS_LOG_2 27
#define MAX_KEY_LOG_2 23
#define NUM_BUCKETS_LOG_2 10
#endif

/*************/
/*  CLASS D  */
/*************/
#if CLASS == 'D'
#define TOTAL_KEYS_LOG_2 31
#define MAX_KEY_LOG_2 27
#define NUM_BUCKETS_LOG_2 10
#endif

#if CLASS == 'D'
#define TOTAL_KEYS (1L << TOTAL_KEYS_LOG_2)
#else
#define TOTAL_KEYS (1 << TOTAL_KEYS_LOG_2)
#endif
#define MAX_KEY (1 << MAX_KEY_LOG_2)
#define NUM_BUCKETS (1 << NUM_BUCKETS_LOG_2)
#define NUM_KEYS TOTAL_KEYS
#define SIZE_OF_BUFFERS NUM_KEYS

#define MAX_ITERATIONS 10
#define TEST_ARRAY_SIZE 5

/*************************************/
/* Typedef: if necessary, change the */
/* size of int here by changing the  */
/* int type to, say, long            */
/*************************************/
#if CLASS == 'D'
typedef long INT_TYPE;
#else
typedef int INT_TYPE;
#endif

/********************/
/* Some global info */
/********************/
INT_TYPE *key_buff_ptr_global; /* used by full_verify to get */
                               /* copies of rank info        */

int passed_verification;

/************************************/
/* These are the three main arrays. */
/* See SIZE_OF_BUFFERS def above    */
/************************************/
INT_TYPE key_array[SIZE_OF_BUFFERS], key_buff1[MAX_KEY],
    key_buff2[SIZE_OF_BUFFERS], partial_verify_vals[TEST_ARRAY_SIZE];

#ifdef USE_BUCKETS
INT_TYPE bucket_size[NUM_BUCKETS], bucket_ptrs[NUM_BUCKETS];
#endif

/**********************/
/* Partial verif info */
/**********************/
INT_TYPE test_index_array[TEST_ARRAY_SIZE], test_rank_array[TEST_ARRAY_SIZE],

    S_test_index_array[TEST_ARRAY_SIZE] = {48427, 17148, 23627, 62548, 4431},
    S_test_rank_array[TEST_ARRAY_SIZE] = {0, 18, 346, 64917, 65463},

    W_test_index_array[TEST_ARRAY_SIZE] = {357773, 934767, 875723, 898999,
                                           404505},
    W_test_rank_array[TEST_ARRAY_SIZE] = {1249, 11698, 1039987, 1043896,
                                          1048018},

    A_test_index_array[TEST_ARRAY_SIZE] = {2112377, 662041, 5336171, 3642833,
                                           4250760},
    A_test_rank_array[TEST_ARRAY_SIZE] = {104, 17523, 123928, 8288932, 8388264},

    B_test_index_array[TEST_ARRAY_SIZE] = {41869, 812306, 5102857, 18232239,
                                           26860214},
    B_test_rank_array[TEST_ARRAY_SIZE] = {33422937, 10244, 59149, 33135281, 99},

    C_test_index_array[TEST_ARRAY_SIZE] = {44172927, 72999161, 74326391,
                                           129606274, 21736814},
    C_test_rank_array[TEST_ARRAY_SIZE] = {61147, 882988, 266290, 133997595,
                                          133525895},

    D_test_index_array[TEST_ARRAY_SIZE] = {1317351170, 995930646, 1157283250,
                                           1503301535, 1453734525},
    D_test_rank_array[TEST_ARRAY_SIZE] = {1, 36538729, 1978098519, 2145192618,
                                          2147425337};

/***********************/
/* function prototypes */
/***********************/
void full_verify(void)
{
    INT_TYPE i, j;

    j = 0;
    for (i = 1; i < NUM_KEYS; i++) {
        if (key_array[i - 1] > key_array[i])
            j++;
    }

    if (j != 0) {
        printf("j: %ld\n", (long)j);
    }
    else
        printf("nope\n");
}

int main(int argc, char **argv)
{
    full_verify();
    return 0;
}
