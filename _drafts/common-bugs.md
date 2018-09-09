---
layout: post
comments: true
title: "Common programmation errors"
tags: [programming, bugs]
---

## Out of bounds

## Signedness

```
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

    if (d <= TOTAL_ELEMENTS) {
        printf("BINGO!\n");
    }
}
```

```
$ gcc -Wall -pedantic -Wconversion -Wextra public/code/unsigned.c -o public/code/unsigned
public/code/unsigned.c: In function ‘main’:
public/code/unsigned.c:17:11: warning: comparison between signed and unsigned integer expressions [-Wsign-compare]
     if (d <= TOTAL_ELEMENTS) {
``` 

```
$ objdump --no-show-raw-insn -d public/code/unsigned -j .text  | sed -n '/main>:/,/^$/p' | grep "^ " | cut -f2,3 > /tmp/nocast.txt
$ diff -Nur /tmp/cast.txt /tmp/nocast.txt
--- /tmp/cast.txt       2018-09-09 21:33:02.348359652 +0200
+++ /tmp/nocast.txt     2018-09-09 21:32:50.988501509 +0200
@@ -2,12 +2,13 @@
 mov    %rsp,%rbp
 sub    $0x10,%rsp
 movl   $0xffffffff,-0x4(%rbp)
-cmpl   $0x3,-0x4(%rbp)
-jg     117b <main+0x21>
-lea    0xe8e(%rip),%rdi        # 2004 <_IO_stdin_used+0x4>
+mov    -0x4(%rbp),%eax
+cmp    $0x3,%eax
+ja     117d <main+0x23>
+lea    0xe8c(%rip),%rdi        # 2004 <_IO_stdin_used+0x4>
 callq  1030 <puts@plt>
 mov    $0x0,%eax
 leaveq
 retq
 nopw   %cs:0x0(%rax,%rax,1)
-nopl   0x0(%rax)
+xchg   %ax,%ax
```

[WTF is nopl](https://stackoverflow.com/questions/12559475/what-does-nopl-do-in-x86-system)

the culprit is the [``ja`` and ``jg`` instructions](http://unixwiz.net/techtips/x86-jumps.html)


## Links

 - [SEI CERT C Coding Standard](https://wiki.sei.cmu.edu/confluence/display/c/SEI+CERT+C+Coding+Standard)
