/*
 * SEE: https://github.com/systems-nuts/unifico/issues/134
 */

typedef enum { false, true } logical;

void simple(int n) { return; }

int main()
{
    logical verified;

    simple(0);
    verified = true;

    if (verified) {
        verified = false;
    }

    return 0;
}
