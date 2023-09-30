#include <stdio.h>

#define CLASS 'S'
#define COMPILETIME "03 Nov 2017"
#define NPBVERSION "3.3.1"
#define CC "gcc"
#define CFLAGS "-g -Wall -O3 -mcmodel=medium"
#define CLINK "$(CC)"
#define CLINKFLAGS "-O3 -mcmodel=medium"
#define C_LIB "-lm"
#define C_INC "-I../common"

void results(char *name, char class, int n1, int n2, int n3, int niter,
             double t, double mops, char *optype, int passed_verification,
             char *npbversion, char *compiletime, char *cc, char *clink,
             char *c_lib, char *c_inc, char *cflags, char *clinkflags)
{
    printf("%c\n", class);
    if (n3 == 0) {
        n3++;
    }
    else
        printf("%4dx%4dx%4d\n", n1, n2, n3);
}

int main()
{

    double timecounter = 0.0;

    results("IS", CLASS, 1, 64, 0, 3, timecounter, 1.0, "keys ranked", 1,
            NPBVERSION, COMPILETIME, CC, CLINK, C_LIB, C_INC, CFLAGS,
            CLINKFLAGS);

    return 0;
}
