#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>


#define MAX_SIZE 128


void read_really_secure(int count) {
    char buffer[MAX_SIZE];

    if (count > MAX_SIZE) {
        return;
    }
    fprintf(stderr, "[+] memsetting...");
    memset(buffer, 'A', count);

    fprintf(stderr, "%d bytes\n", count);

    fprintf(stdout, buffer);
}

#define COUNT 128U

void really_smth(int count) {
    while(count-- >= 0U)
        fprintf(stdout, "%c", count);
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        fprintf(stderr, "usage: %s <n>\n", argv[0]);
        exit(1);
    }

    int n = atoi(argv[1]);

    //read_really_secure(n);
    really_smth(n);

    return 0;
}
