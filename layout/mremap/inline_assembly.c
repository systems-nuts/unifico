int main()
{
    int a = 10, b;

    asm("movl %1, %%r9d; \n\t"
        "movl %%r9d, %0;"
        : "=r"(b) /* output */
        : "r"(a)  /* input */
        : "%r9d"  /* clobbered register */
    );
}
