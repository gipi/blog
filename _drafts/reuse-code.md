---
layout: post
comments: true
title: "Reuse raw binary code"
tags: [ELF, reversing, internal]
---

Imagine to have a challenge, like a firmware, in a raw binary format; imagine
that you have to find out the generated passcode but you cannot debug the
code running live.

The idea here is to extract the code that you want to run and to transplant it
into an our executable.

## 

```asm
BITS 32

            org     0x08048000

ehdr:                                                 ; Elf32_Ehdr
            db      0x7F, "ELF", 1, 1, 1, 0         ;   e_ident
    times 8 db      0
            dw      2                               ;   e_type
            dw      3                               ;   e_machine
            dd      1                               ;   e_version
            dd      _start                          ;   e_entry
            dd      phdr - $$                       ;   e_phoff
            dd      0                               ;   e_shoff
            dd      0                               ;   e_flags
            dw      ehdrsize                        ;   e_ehsize
            dw      phdrsize                        ;   e_phentsize
            dw      1                               ;   e_phnum
            dw      0                               ;   e_shentsize
            dw      0                               ;   e_shnum
            dw      0                               ;   e_shstrndx

ehdrsize      equ     $ - ehdr

phdr:                                                 ; Elf32_Phdr
            dd      1                               ;   p_type
            dd      0                               ;   p_offset
            dd      $$                              ;   p_vaddr
            dd      $$                              ;   p_paddr
            dd      filesize                        ;   p_filesz
            dd      filesize                        ;   p_memsz
            dd      5                               ;   p_flags
            dd      0x1000                          ;   p_align

phdrsize      equ     $ - phdr

_start:

; your program here

filesize      equ     $ - $$
```
    $ nasm -f bin -o /tmp/elf.bin /tmp/elf.asm

```python
from elf.elf_binary import Elf
binary = Elf('/tmp/elf.bin', access='w')
from elf.elf_header import ehdr_machine
binary.header.e_machine = ehdr_machine['EM_AVR']
binary.write()
```

## X86
```
void foobar();


unsigned long g_flag = 0xdeadbeef;

void bau(short value) {
    g_flag = value - 1;
    foobar();
}
```

and compile it with ``gcc -Wall -m32 -c test.c``; the resulting object file
will contain the following code for the ``bau()`` function.

```
$ objdump -j .text -D test.o

test.o:     formato del file elf32-i386


Disassemblamento della sezione .text:

00000000 <bau>:
   0:   55                      push   %ebp
   1:   89 e5                   mov    %esp,%ebp
   3:   53                      push   %ebx
   4:   83 ec 14                sub    $0x14,%esp
   7:   e8 fc ff ff ff          call   8 <bau+0x8>
   c:   05 01 00 00 00          add    $0x1,%eax
  11:   8b 55 08                mov    0x8(%ebp),%edx
  14:   66 89 55 f4             mov    %dx,-0xc(%ebp)
  18:   0f bf 55 f4             movswl -0xc(%ebp),%edx
  1c:   83 ea 01                sub    $0x1,%edx
  1f:   89 d1                   mov    %edx,%ecx
  21:   8b 90 00 00 00 00       mov    0x0(%eax),%edx
  27:   89 0a                   mov    %ecx,(%edx)
  29:   89 c3                   mov    %eax,%ebx
  2b:   e8 fc ff ff ff          call   2c <bau+0x2c>
  30:   90                      nop
  31:   83 c4 14                add    $0x14,%esp
  34:   5b                      pop    %ebx
  35:   5d                      pop    %ebp
  36:   c3                      ret
```

with the following relocation

```
$ readelf -r test.o

La sezione di rilocazione '.rel.text' all'offset 0x220 contiene 4 voci:
 Offset     Info    Tipo            Valore sim Nome sim
00000008  00000c02 R_386_PC32        00000000   __x86.get_pc_thunk.ax
0000000d  00000d0a R_386_GOTPC       00000000   _GLOBAL_OFFSET_TABLE_
00000023  00000a2b R_386_GOT32X      00000004   g_flag
0000002c  00000e04 R_386_PLT32       00000000   foobar
```


```
$ nm test.o
00000000 T bau
         U foobar
00000000 D g_flag
         U _GLOBAL_OFFSET_TABLE_
00000000 T __x86.get_pc_thunk.ax
```

```
struct Rel { 
    uint32    r_offset; 
    uint24    r_sym_index; 
    uint8     r_type; 
}; 
enum for t_type { 
    R_386_32=1, 
    R_386_GOT32=3, 
    R_386_PLT32=4, 
    R_386_COPY=5, 
    R_386_GLOB_DAT=6, 
    R_386_JUMP_SLOT=7, 
    R_386_RELATIVE=8, 
    R_386_GOTOFF=9, 
    R_386_GOTPC=10 
};
```

    What is a reloc? Binary executables often need certain bits of information fixed up before they execute.
    ELF binaries carry a list of relocs which describe these fixups. Each reloc contains: 
      the address in the binary that is to get the fixup (offset) 
      the algorithm to calculate the fixup (type) 
      a symbol (string and object len) 

    At fixup time, the algorithm uses the offset & symbol, along with the value
    currently in the file, to calculate a new value to be deposited into memory.

``e8fcffffff`` is the opcode for a relative jump: the encoding is ``e8<little endian 32 bits address>``
so in our case is ``call 0xfffffffc`` that using two's complement gives us ``call -4``, but the actual base
for the offset is the address of the following instruction: since the opcode for the ``call`` instruction takes
5 bytes, we have as final address ``0xc - 4 = 8`` that is the value of the disassembled code.

Similarly ``05100000`` is the opcode for ``add $1, eax`` that has the general form ``05 <little endian 32bit value>``
for ``add <32 bit value>, eax``.

```
$ readelf -x .data test.o

Dump esadecimale della sezione ".data":
  0x00000000 efbeadde                            ....
```

```
$ objdump -D -j .text /tmp/auaua| sed '/<bau>:/,/^$/!d'
0000053b <bau>:
 53b:   55                      push   %ebp
 53c:   89 e5                   mov    %esp,%ebp
 53e:   53                      push   %ebx
 53f:   83 ec 14                sub    $0x14,%esp
 542:   e8 f0 ff ff ff          call   537 <__x86.get_pc_thunk.ax>
 547:   05 b9 1a 00 00          add    $0x1ab9,%eax
 54c:   8b 55 08                mov    0x8(%ebp),%edx
 54f:   66 89 55 f4             mov    %dx,-0xc(%ebp)
 553:   0f bf 55 f4             movswl -0xc(%ebp),%edx
 557:   83 ea 01                sub    $0x1,%edx
 55a:   89 d1                   mov    %edx,%ecx
 55c:   8d 90 1c 00 00 00       lea    0x1c(%eax),%edx
 562:   89 0a                   mov    %ecx,(%edx)
 564:   89 c3                   mov    %eax,%ebx
 566:   e8 bc ff ff ff          call   527 <foobar>
 56b:   90                      nop
 56c:   83 c4 14                add    $0x14,%esp
 56f:   5b                      pop    %ebx
 570:   5d                      pop    %ebp
 571:   c3                      ret
```

## AVR

The relocatable object file has the following code

```
00000000 <bau>:
   0:   cf 93           push    r28
   2:   df 93           push    r29
   4:   00 d0           rcall   .+0             ; 0x6 <bau+0x6>
   6:   cd b7           in      r28, 0x3d       ; 61
   8:   de b7           in      r29, 0x3e       ; 62
   a:   9a 83           std     Y+2, r25        ; 0x02
   c:   89 83           std     Y+1, r24        ; 0x01
   e:   89 81           ldd     r24, Y+1        ; 0x01
  10:   9a 81           ldd     r25, Y+2        ; 0x02
  12:   01 97           sbiw    r24, 0x01       ; 1
  14:   09 2e           mov     r0, r25
  16:   00 0c           add     r0, r0
  18:   aa 0b           sbc     r26, r26
  1a:   bb 0b           sbc     r27, r27
  1c:   80 93 00 00     sts     0x0000, r24     ; 0x800000 <__SREG__+0x7fffc1>
  20:   90 93 00 00     sts     0x0000, r25     ; 0x800000 <__SREG__+0x7fffc1>
  24:   a0 93 00 00     sts     0x0000, r26     ; 0x800000 <__SREG__+0x7fffc1>
  28:   b0 93 00 00     sts     0x0000, r27     ; 0x800000 <__SREG__+0x7fffc1>
  2c:   00 d0           rcall   .+0             ; 0x2e <bau+0x2e>
  2e:   00 00           nop
  30:   0f 90           pop     r0
  32:   0f 90           pop     r0
  34:   df 91           pop     r29
  36:   cf 91           pop     r28
  38:   08 95           ret
```

```
$ readelf -r test-avr.o

La sezione di rilocazione '.rela.text' all'offset 0x1d0 contiene 6 voci:
 Offset     Info    Tipo            Valore sim  Nome sim + Addendo
00000004  00000203 R_AVR_13_PCREL    00000000   .text + 6
0000001e  00000b04 R_AVR_16          00000001   g_flag + 0
00000022  00000b04 R_AVR_16          00000001   g_flag + 1
00000026  00000b04 R_AVR_16          00000001   g_flag + 2
0000002a  00000b04 R_AVR_16          00000001   g_flag + 3
0000002c  00000d03 R_AVR_13_PCREL    00000000   foobar + 0
```

and the final file instead

```
00000038 <bau>:
  38:   cf 93           push    r28
  3a:   df 93           push    r29
  3c:   00 d0           rcall   .+0             ; 0x3e <__SP_H__>
  3e:   cd b7           in      r28, 0x3d       ; 61
  40:   de b7           in      r29, 0x3e       ; 62
  42:   9a 83           std     Y+2, r25        ; 0x02
  44:   89 83           std     Y+1, r24        ; 0x01
  46:   89 81           ldd     r24, Y+1        ; 0x01
  48:   9a 81           ldd     r25, Y+2        ; 0x02
  4a:   01 97           sbiw    r24, 0x01       ; 1
  4c:   09 2e           mov     r0, r25
  4e:   00 0c           add     r0, r0
  50:   aa 0b           sbc     r26, r26
  52:   bb 0b           sbc     r27, r27
  54:   80 93 60 00     sts     0x0060, r24     ; 0x800060 <_edata>
  58:   90 93 61 00     sts     0x0061, r25     ; 0x800061 <_edata+0x1>
  5c:   a0 93 62 00     sts     0x0062, r26     ; 0x800062 <_edata+0x2>
  60:   b0 93 63 00     sts     0x0063, r27     ; 0x800063 <_edata+0x3>
  64:   e1 df           rcall   .-62            ; 0x28 <foobar>
  66:   00 00           nop
  68:   0f 90           pop     r0
  6a:   0f 90           pop     r0
  6c:   df 91           pop     r29
  6e:   cf 91           pop     r28
  70:   08 95           ret
```

be aware that ``objdump`` mixes hexadecimal and decimal representation of numbers
so ``rcall .-62`` means ``0x64 - 62 = 0x28``.

 - [BFD for AVR](https://github.com/bminor/binutils-gdb/blob/master/bfd/elf32-avr.c)
 - https://github.com/mohamed-anwar/avr-tcc/blob/master/elf.h

## Reconstruct a relocatable object

We need at least

 - ``BSS`` section
 - ``TEXT`` section
 - ``RELA`` section
 - ``SYMTAB`` section

## Links

 - [Study of ELF loading and relocs](http://netwinder.osuosl.org/users/p/patb/public_html/elf_relocs.html)
 - [slides](http://www.scs.stanford.edu/15au-cs140/notes/linking-print.pdf) about the internal of the linking process
 - [32-bit x86: Relocation Types](https://docs.oracle.com/cd/E19120-01/open.solaris/819-0690/chapter6-26/index.html)
 - [X86 Opcode and Instruction Reference](http://ref.x86asm.net/coder32.html)
