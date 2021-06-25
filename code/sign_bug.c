#include <stdio.h>
#include <stdlib.h>

#define MAX_COUNT 127

struct profile {
    char name[16];
    char surname[16];
};

void usage(const char progname[]) {
    fprintf(stderr, "usage: %s <count>\n", progname);
    exit(0);
}

void parse(unsigned int size) {
    unsigned int cycle;
    struct profile* guestbook = malloc(size);

    fprintf(stderr, "struct profile* = %p\n", guestbook);

#if 0
    for (cycle = 0 ; cycle < count ; cycle++) {
        read(STDIN_FILENO, )
    }
#endif
}

enum { INTBUFSIZE = 1 };
 
extern int getdata(void);
int buf[INTBUFSIZE];
  

int getdata() {
    return 0xdeadbeef;
}

void func(void) {
  int *buf_ptr = buf;
 
    fprintf(stderr, "buf               = %p\n", buf);
    fprintf(stderr, "buf + sizeof(buf) = %p\n", buf + sizeof(buf));
    fprintf(stderr, "buf + INTBUFSIZE  = %p\n", buf + INTBUFSIZE);
  while (buf_ptr < (buf + sizeof(buf))) {
    *buf_ptr++ = getdata();
  }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        usage(argv[0]);
    }

    int count = atoi(argv[1]);

    /*
     * sizeof struct profile is 32 bytes, i.e. 2^5,
     * this means that we have a "margin" of 5 bits
     * to play with!
     *
     * The dimension of count is 32 bits, so passing as
     * argument to the application something big as 2^(32 - 5)
     * we obtain an overflow.
     */ 
    fprintf(stderr, "sizeof(struct profile)=%lu\n", sizeof(struct profile));
    fprintf(stderr, "sizeof(count)=%lu\n", sizeof(count));
    fprintf(stderr, "count=%d\n", count);

    /*
     * multiplying them is equivalent to shift by
     * 5 bits the variable "count".
     *
     * Since we have an upper limit given by 127, i.e. 2^7 - 1,
     * if we set count=
     */
    int size = count * sizeof(struct profile);

    fprintf(stderr, "size=%d\n", size);

    if (size < 0 || size > MAX_COUNT) {
        fprintf(stderr, " [E] size must be positive and less than %d\n", MAX_COUNT);
        exit(1);
    }

    parse(size);

    func();

}
