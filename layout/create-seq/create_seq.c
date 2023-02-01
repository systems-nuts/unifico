#include <stdio.h>

#define MAX_KEY_LOG_2 21
#define MAX_KEY (1 << MAX_KEY_LOG_2)

#define TOTAL_KEYS_LOG_2 25
#define TOTAL_KEYS (1 << TOTAL_KEYS_LOG_2)
#define NUM_KEYS TOTAL_KEYS

#define SIZE_OF_BUFFERS NUM_KEYS

int key_array[SIZE_OF_BUFFERS];

double randlc(double *X, double *A) { return (*X) * (*A); }

void create_seq(double seed, double a)
{
    double x;
    int i;
    int k;
    long long l;

    k = MAX_KEY / 4;

    // Small immediate
    for (i = 0; i < 4095; i++) {
        x = randlc(&seed, &a);
        key_array[i] = k * x;
    }

    // Medium immediate
    for (i = 0; i < NUM_KEYS; i++) {
        x = randlc(&seed, &a);
        key_array[i] = k * x;
    }

    // 12-shift immediate
    for (i = 0; i < 4096 * 3; i++) {
        x = randlc(&seed, &a);
        key_array[i % 2] = k * x;
    }

    // 12-shift immediate plus one
    for (i = 0; i < 4096 * 3 + 1; i++) {
        x = randlc(&seed, &a);
        key_array[i % 4] = k * x;
    }

    // Large immediate
    for (l = 0; l < 100000000000; l++) {
        x = randlc(&seed, &a);
        key_array[l % 5] = k * x;
    }
}

int main()
{
    create_seq(3.0, 4.0);
    return 0;
}
