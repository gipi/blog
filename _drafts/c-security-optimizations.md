---
layout: post
comments: true
title: "Go home C you are drunk"
tags: [C, programming, security, compiler]
---

This post is the result of this [tweet](https://twitter.com/andreasdotorg/status/992290533585256449)
at the end the claim was erroneus but the spark continues

```
#define SIZE 8192

char buf[SIZE];

void cpy(struct foo* p, int count) {
    int n = count * sizeof(struct foo);
    fprintf(stderr, "n=(%i) %u ", n, n);
    if ((n < SIZE) && (n > 0)) {
        fprintf(stderr, "copying");

        memcpy(buf, p, n);
    }
    fprintf(stderr, "\n");
}
```

``-O0``

```
(gdb) disassemble cpy
Dump of assembler code for function cpy:
   0x00000000000007ba <+0>:     push   %rbp
   0x00000000000007bb <+1>:     mov    %rsp,%rbp
   0x00000000000007be <+4>:     sub    $0x20,%rsp
   0x00000000000007c2 <+8>:     mov    %rdi,-0x18(%rbp)
   0x00000000000007c6 <+12>:    mov    %esi,-0x1c(%rbp)
   0x00000000000007c9 <+15>:    mov    -0x1c(%rbp),%eax
   0x00000000000007cc <+18>:    cltq
   0x00000000000007ce <+20>:    add    %eax,%eax
   0x00000000000007d0 <+22>:    mov    %eax,-0x4(%rbp)
   0x00000000000007d3 <+25>:    mov    0x200886(%rip),%rax        # 0x201060 <stderr@@GLIBC_2.2.5>
   0x00000000000007da <+32>:    mov    -0x4(%rbp),%ecx
   0x00000000000007dd <+35>:    mov    -0x4(%rbp),%edx
   0x00000000000007e0 <+38>:    lea    0x13d(%rip),%rsi        # 0x924
   0x00000000000007e7 <+45>:    mov    %rax,%rdi
   0x00000000000007ea <+48>:    mov    $0x0,%eax
   0x00000000000007ef <+53>:    callq  0x660 <fprintf@plt>
   0x00000000000007f4 <+58>:    cmpl   $0x1fff,-0x4(%rbp)
   0x00000000000007fb <+65>:    jg     0x83c <cpy+130>
   0x00000000000007fd <+67>:    cmpl   $0x0,-0x4(%rbp)
   0x0000000000000801 <+71>:    jle    0x83c <cpy+130>
   0x0000000000000803 <+73>:    mov    0x200856(%rip),%rax        # 0x201060 <stderr@@GLIBC_2.2.5>
   0x000000000000080a <+80>:    mov    %rax,%rcx
   0x000000000000080d <+83>:    mov    $0x7,%edx
   0x0000000000000812 <+88>:    mov    $0x1,%esi
   0x0000000000000817 <+93>:    lea    0x111(%rip),%rdi        # 0x92f
   0x000000000000081e <+100>:   callq  0x690 <fwrite@plt>
   0x0000000000000823 <+105>:   mov    -0x4(%rbp),%eax
   0x0000000000000826 <+108>:   movslq %eax,%rdx
   0x0000000000000829 <+111>:   mov    -0x18(%rbp),%rax
   0x000000000000082d <+115>:   mov    %rax,%rsi
   0x0000000000000830 <+118>:   lea    0x200849(%rip),%rdi        # 0x201080 <buf>
   0x0000000000000837 <+125>:   callq  0x670 <memcpy@plt>
   0x000000000000083c <+130>:   mov    0x20081d(%rip),%rax        # 0x201060 <stderr@@GLIBC_2.2.5>
   0x0000000000000843 <+137>:   mov    %rax,%rsi
   0x0000000000000846 <+140>:   mov    $0xa,%edi
   0x000000000000084b <+145>:   callq  0x650 <fputc@plt>
   0x0000000000000850 <+150>:   nop
   0x0000000000000851 <+151>:   leaveq
   0x0000000000000852 <+152>:   retq
```

``-O3``

```
(gdb) disassemble cpy
Dump of assembler code for function cpy:
   0x00000000000007f0 <+0>:     push   %rbp
   0x00000000000007f1 <+1>:     push   %rbx
   0x00000000000007f2 <+2>:     mov    %rdi,%rbp
   0x00000000000007f5 <+5>:     lea    (%rsi,%rsi,1),%ebx  ; 
   0x00000000000007f8 <+8>:     lea    0xf5(%rip),%rsi        # 0x8f4
   0x00000000000007ff <+15>:    xor    %eax,%eax
   0x0000000000000801 <+17>:    sub    $0x8,%rsp
   0x0000000000000805 <+21>:    mov    0x200854(%rip),%rdi        # 0x201060 <stderr@@GLIBC_2.2.5>
   0x000000000000080c <+28>:    mov    %ebx,%ecx
   0x000000000000080e <+30>:    mov    %ebx,%edx
   0x0000000000000810 <+32>:    callq  0x660 <fprintf@plt>
   0x0000000000000815 <+37>:    lea    -0x1(%rbx),%eax      ; 
   0x0000000000000818 <+40>:    cmp    $0x1ffe,%eax
   0x000000000000081d <+45>:    ja     0x84e <cpy+94>
   0x000000000000081f <+47>:    mov    0x20083a(%rip),%rcx        # 0x201060 <stderr@@GLIBC_2.2.5>
   0x0000000000000826 <+54>:    lea    0xd2(%rip),%rdi        # 0x8ff
   0x000000000000082d <+61>:    mov    $0x7,%edx
   0x0000000000000832 <+66>:    mov    $0x1,%esi
   0x0000000000000837 <+71>:    callq  0x690 <fwrite@plt>
   0x000000000000083c <+76>:    lea    0x20083d(%rip),%rdi        # 0x201080 <buf>
   0x0000000000000843 <+83>:    movslq %ebx,%rdx             ; 
   0x0000000000000846 <+86>:    mov    %rbp,%rsi
   0x0000000000000849 <+89>:    callq  0x670 <memcpy@plt>
   0x000000000000084e <+94>:    mov    0x20080b(%rip),%rsi        # 0x201060 <stderr@@GLIBC_2.2.5>
   0x0000000000000855 <+101>:   add    $0x8,%rsp
   0x0000000000000859 <+105>:   mov    $0xa,%edi
   0x000000000000085e <+110>:   pop    %rbx
   0x000000000000085f <+111>:   pop    %rbp
   0x0000000000000860 <+112>:   jmpq   0x650 <fputc@plt>
```

```
$ gcc -v
Using built-in specs.
COLLECT_GCC=gcc
COLLECT_LTO_WRAPPER=/usr/lib/gcc/x86_64-linux-gnu/7/lto-wrapper
OFFLOAD_TARGET_NAMES=nvptx-none
OFFLOAD_TARGET_DEFAULT=1
Target: x86_64-linux-gnu
Configured with: ../src/configure -v --with-pkgversion='Debian 7.2.0-19' --with-bugurl=file:///usr/share/doc/gcc-7/README.Bugs --enable-languages=c,ada,c++,go,brig,d,fortran,objc,obj-c++ --prefix=/usr --with-gcc-major-version-only --program-suffix=-7 --program-prefix=x86_64-linux-gnu- --enable-shared --enable-linker-build-id --libexecdir=/usr/lib --without-included-gettext --enable-threads=posix --libdir=/usr/lib --enable-nls --with-sysroot=/ --enable-clocale=gnu --enable-libstdcxx-debug --enable-libstdcxx-time=yes --with-default-libstdcxx-abi=new --enable-gnu-unique-object --disable-vtable-verify --enable-libmpx --enable-plugin --enable-default-pie --with-system-zlib --with-target-system-zlib --enable-objc-gc=auto --enable-multiarch --disable-werror --with-arch-32=i686 --with-abi=m64 --with-multilib-list=m32,m64,mx32 --enable-multilib --with-tune=generic --enable-offload-targets=nvptx-none --without-cuda-driver --enable-checking=release --build=x86_64-linux-gnu --host=x86_64-linux-gnu --target=x86_64-linux-gnu
Thread model: posix
gcc version 7.2.0 (Debian 7.2.0-19)
```

CF = 0 and ZF = 0

 - ``CF`` is the **carry flag**
 - ``ZF`` is the **zero flag**

 - [Intel x86 JUMP quick reference](http://unixwiz.net/techtips/x86-jumps.html)
 - [The Correctness-Security Gap in Compiler Optimization](https://nebelwelt.net/publications/files/15LangSec.pdf)
 - [Insecure Compiler Optimization](https://www.owasp.org/index.php/Insecure_Compiler_Optimization)
 - [Undefined Behavior: What Happened to My Code?](https://pdos.csail.mit.edu/papers/ub:apsys12.pdf)
 - [STACK](https://github.com/xiw/stack/) A static checker for identifying unstable code
