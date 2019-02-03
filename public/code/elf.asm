; a mini ELF
; nasm -o public/code/elf public/code/elf.asm

; https://www.nasm.us/xdoc/2.14.02/html/nasmdoc4.html

; Ange Albertini, BSD Licence 2014-2017

BITS 32

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

EI_NIDENT equ 16

struc Elf32_Ehdr
    .e_ident     resb EI_NIDENT
    .e_type      resw 1
    .e_machine   resw 1
    .e_version   resd 1
    .e_entry     resd 1
    .e_phoff     resd 1
    .e_shoff     resd 1
    .e_flags     resd 1
    .e_ehsize    resw 1
    .e_phentsize resw 1
    .e_phnum     resw 1
    .e_shentsize resw 1
    .e_shnum     resw 1
    .e_shstrndx  resw 1
endstruc

struc Elf32_Shdr
    .sh_name    resd 1
    .sh_type    resd 1
    .sh_flags   resd 1
    .sh_addr    resd 1
    .sh_offset  resd 1
    .sh_size    resd 1
    .sh_link    resd 1
    .sh_info    resd 1
    .sh_addralign resd 1
    .sh_entsize resd 1
endstruc

struc Elf32_Phdr
    .p_type   resd 1
    .p_offset resd 1
    .p_vaddr  resd 1
    .p_paddr  resd 1
    .p_filesz resd 1
    .p_memsz  resd 1
    .p_flags  resd 1
    .p_align  resd 1
endstruc

struc Elf32_Sym
    .st_name  resd 1
    .st_value resd 1
    .st_size  resd 1
    .st_info  resb 1
    .st_other resb 1
    .st_shndx resw 1
endstruc

struc Elf32_Rela
    .r_offset resd 1
    .r_info   resd 1
    .r_addend resd 1
endstruc

ELFCLASS32 equ 1

ELFDATA2LSB equ 1

EV_CURRENT equ 1

ET_EXEC equ 2

EM_386 equ 3

PT_LOAD equ 1

PF_X equ 1
PF_R equ 4

SHT_SYMTAB equ  2
SHT_STRTAB equ  3
SHT_RELA   equ  4
SHT_REL    equ  9

SC_EXIT equ 1

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

ELFBASE equ 08000000h

org ELFBASE

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; ELF Header

segment_start:

ehdr:
istruc Elf32_Ehdr
    at Elf32_Ehdr.e_ident
        EI_MAG     db 07Fh, "ELF"
        EI_CLASS   db ELFCLASS32
        EI_DATA    db ELFDATA2LSB
        EI_VERSION db EV_CURRENT
    at Elf32_Ehdr.e_type,      dw ET_EXEC
    at Elf32_Ehdr.e_machine,   dw EM_386
    at Elf32_Ehdr.e_version,   dd EV_CURRENT
    at Elf32_Ehdr.e_entry,     dd entry
    at Elf32_Ehdr.e_phoff,     dd phdr - ehdr
    at Elf32_Ehdr.e_shoff,     dd shdr - ehdr
    at Elf32_Ehdr.e_ehsize,    dw Elf32_Ehdr_size
    at Elf32_Ehdr.e_phentsize, dw Elf32_Phdr_size
    at Elf32_Ehdr.e_phnum,     dw PHNUM
    at Elf32_Ehdr.e_shentsize, dw Elf32_Shdr_size
    at Elf32_Ehdr.e_shnum,     dw SHNUM
    at Elf32_Ehdr.e_shstrndx,  dw 1
iend
align 16, db 0

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Program header table

phdr:
istruc Elf32_Phdr
    at Elf32_Phdr.p_type,   dd PT_LOAD
    at Elf32_Phdr.p_offset, dd segment_start - ehdr
    at Elf32_Phdr.p_vaddr,  dd ELFBASE
    at Elf32_Phdr.p_paddr,  dd ELFBASE
    at Elf32_Phdr.p_filesz, dd SEGMENT_SIZE
    at Elf32_Phdr.p_memsz,  dd SEGMENT_SIZE
    at Elf32_Phdr.p_flags,  dd PF_R + PF_X
iend
PHNUM equ ($ - phdr) / Elf32_Phdr_size
align 16, db 0


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Section header table

; below we create three sections

shdr:
; relocation section header
istruc Elf32_Shdr
    at Elf32_Shdr.sh_name,    dd _rel_section_name - strtab
    at Elf32_Shdr.sh_type,    dd SHT_RELA
    at Elf32_Shdr.sh_flags,   dd 0
    at Elf32_Shdr.sh_addr,    dd 0
    at Elf32_Shdr.sh_offset,  dd rela - ehdr
    at Elf32_Shdr.sh_size,    dd RELA_SIZE
    at Elf32_Shdr.sh_link,    dd 2
    at Elf32_Shdr.sh_entsize, dd Elf32_Rela_size
iend
; string table section header
istruc Elf32_Shdr
    at Elf32_Shdr.sh_name,   dd _strsec_section_name - strtab
    at Elf32_Shdr.sh_type,   dd SHT_STRTAB
    at Elf32_Shdr.sh_flags,  dd 0
    at Elf32_Shdr.sh_addr,   dd 0
    at Elf32_Shdr.sh_offset, dd strtab - ehdr
    at Elf32_Shdr.sh_size,   dd STRTAB_SIZE
iend
; symbol table section header
istruc Elf32_Shdr
    at Elf32_Shdr.sh_name,   dd 0
    at Elf32_Shdr.sh_type,   dd SHT_SYMTAB
    at Elf32_Shdr.sh_flags,  dd 0
    at Elf32_Shdr.sh_addr,   dd 0
    at Elf32_Shdr.sh_offset, dd symtab - ehdr
    at Elf32_Shdr.sh_size,   dd SYMSIZE
    at Elf32_Shdr.sh_link,    dd 1
    at Elf32_Shdr.sh_entsize, dd Elf32_Sym_size
iend
SHNUM equ ($ - shdr) / Elf32_Shdr_size

align 16, db 0

rela:
istruc Elf32_Rela
    at Elf32_Rela.r_offset, dd 4
    at Elf32_Rela.r_info,   dd 0x0002
    at Elf32_Rela.r_addend, dd 8
iend
istruc Elf32_Rela
    at Elf32_Rela.r_offset, dd 2
    at Elf32_Rela.r_info,   dd 0x0103
    at Elf32_Rela.r_addend, dd 6
iend
RELA_SIZE equ ($ - rela)

symtab:
; we define two simbols
istruc Elf32_Sym
    at Elf32_Sym.st_name, dd _strsym_first - strtab
    at Elf32_Sym.st_value,   dd 0
    at Elf32_Sym.st_size,    dd 8
    at Elf32_Sym.st_info,    db 4
    at Elf32_Sym.st_other,   db 0
    at Elf32_Sym.st_shndx,   dw 0
istruc Elf32_Sym
    at Elf32_Sym.st_name, dd _strsym_rel - strtab
    at Elf32_Sym.st_value,   dd 0
    at Elf32_Sym.st_size,    dd 8
    at Elf32_Sym.st_info,    db 4
    at Elf32_Sym.st_other,   db 0
    at Elf32_Sym.st_shndx,   dw 0
iend
SYMSIZE equ ($ - symtab)
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; .text section (code)

text:
entry:
    mov ebx, 42 ; return code

    mov eax, SC_EXIT
    int 80h

TEXT_SIZE equ $ - text

align 16, db 0

SEGMENT_SIZE equ $ - segment_start

strtab:
    db 0x00
_rel_section_name:
    db '.rel.text', 0x00
_strsec_section_name:
    db '.string', 0x00
_strsym_first:
    db 'whatever', 0x00
_strsym_rel:
    db 'auaua', 0x00

STRTAB_SIZE equ $ - strtab
