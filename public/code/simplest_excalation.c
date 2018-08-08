/*
 * gcc -Wall -m32 -no-pie -fno-stack-protector -z execstack public/code/simplest_excalation.c -o public/code/simplest_excalation
 */
#include <stdio.h>
#include <stdlib.h>

#define NAME_LENGTH 32

int main() {
    char name[NAME_LENGTH];

    printf("What's your name? ");
    gets(name);

    printf("hello, %s\n", name);

    return EXIT_SUCCESS;
}
