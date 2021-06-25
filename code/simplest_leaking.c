/*
 * gcc -Wall -m32 -no-pie -fno-stack-protector -z execstack public/code/simplest_leaking.c -o public/code/simplest_leaking
 */
#include <stdio.h>
#include <stdlib.h>

#define NAME_LENGTH 32

void greetings() {
    char name[NAME_LENGTH];
    gets(name);

    printf("hello, ");
    printf(name);
    printf("\n");
}

int main(int argc, char* argv[], char* envp[]) {

    printf("What's your name? ");

    greetings();

    return EXIT_SUCCESS;
}
