/*
 * Expert C programming pg27
 */
#include <stdio.h>

int array[] = {
    1,
    2,
    3
};

#define TOTAL_ELEMENTS (sizeof(array)/sizeof(array[0]))

int main() {
    int d = -1;

    if (d <= (int)TOTAL_ELEMENTS) {
        printf("BINGO!\n");
    }
}
