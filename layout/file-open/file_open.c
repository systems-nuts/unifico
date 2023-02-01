#include <stdio.h>
#include <stdlib.h>

int main()
{
    FILE *fp;

    fp = fopen("file.txt", "w+");
    // printf("boo %d\n", fp);
    fprintf(fp, "%s %s %s %d", "We", "are", "in", 2012);

    fclose(fp);

    return (0);
}
