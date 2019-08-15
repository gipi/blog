---
layout: post
comments: true
title: "ELF file format and a pratical study of the execution view"
tags: [ELF]
---

In the post about [pratical approach to binary exploitation]({% post_url 2018-08-13-pratical-approach-exploitation %})
I talked of how an executable is a memory archive describing a (future) running process. In this post
I want to study how this memory archive is loaded in memory in a Linux system, in particular
my interest will be directed upon the most used format in \*nix system, i.e. the **executable and linkage
format**; it isn't the only format available, for example the Mac OS X uses the Mach format and
the Windows OS uses the PE format.

The actual specification is [here](http://www.sco.com/developers/devspecs/) but take in mind that
each specific architecture has its own addendum to it (I hope will be more clear later) for example
there is the
[Intel386™ Architecture Processor Supplement](http://www.sco.com/developers/devspecs/abi386-4.pdf)
or the [AMD64 supplement](https://www.uclibc.org/docs/psABI-x86_64.pdf).

## What we need from the OS

To understand why the format is the way it is, you need to understand that this
format serves two main scopes: one at compilation time and one at runtime, or
the **linking view** and **execution view**.

In this discussion I'm more interested in the execution view, but I will need to talk
also of the linking view.

To understand which data is needed at runtime I need to describe how an executable
"connects" with the OS (where with "OS" I mean a kernel implementing memory, process and
privileges management, not a real time OS where, I know I'm over-simplfying, is pratically
possible to do anything).

The only way a process can interact with the OS is using the so called **syscalls**, they
are in practice the API of the OS; probably you haven't ever invoked directly a syscall
in your code but used the standard libraries that your distribution provides; if you are
a mainstream person, you are using the glibc as standard C library.

This adds a layer of complexity to all the execution-time concept: who is going to
"connect" the library with your executable? the answer is the **loader**, when the kernel
tries to start an ELF file, it loads the needed segments in memory and then pass the
execution to another program that will "resolve" the missing dots, this is program is
the loader.

This doesn't apply to executable compiled statically, where the "resolution" is done
at compile time and all the libraries are contained in the executable itself.

Obviously the interpreter must be a statically compiled binary otherwise would be
a recursive task to solve.

## First look at an ELF

The binary format is composed of four parts: the **header**, the **section table**,
the **program table** and finally the **sections**.

First of all the specification describes the fundamental data types that
are used on disk


The header simply describes the major information regarding the executable
file, like **entry point**, **architecture**, **endianess** etc...


The sections


Relocation is the process of connecting symbolic references with symbolic
definitions


### Segments

What a program header describes is a segment, a portion of the file comprising
one or more sections, loaded at given address at runtime.

The data type describing it is the following

```
typedef struct{
    Elf32_Word  p_type;
    Elf32_Off   p_offset;
    Elf32_Addr  p_vaddr;
    Elf32_Addr  p_paddr;
    Elf32_Word  p_filesz;
    Elf32_Word  p_memsz;
    Elf32_Word  p_flags;
    Elf32_Word  p_align;
} Elf32_Phdr;
```

(it exists a corresponding struct for 64bit architectures)

| Field | Description |
|-------|-------------|
| ``p_type`` | type of segment (described in the following table) |
| ``p_offset`` | position in the file |
| ``p_vaddr`` | virtual address |
| ``p_paddr`` | physical address |
| ``p_filesz`` | size of the segment in the file |
| ``p_memsz`` | size of the segment in memory |
| ``p_flags`` | indicate RWX permissions |
| ``p_align`` | indicate the alignment |

| Type | Descriptor |
|------|------------|
| ``PT_NULL``    | this entry can be ignored                |
| ``PT_LOAD``    | loadable segment                         |
| ``PT_DYNAMIC`` | contains the dynamic linking information |
| ``PT_INTERP``  | contains the path of the interpreter.    |
| ``PT_NOTE``    |  contains auxiliary information          |
| ``PT_SHLIB``   | reserved                                 |
| ``PT_PHDR``    | indicates the program header             |

## Look Ma' the code

If you want to know precisely how the kernel loads the ELF and calls the executable,
wait no more and look at ``fs/binfmt_elf.c`` in the Linux source code: below the stripped down code
where is clear that the kernel loads the interpreter and the passes to it
the execution (look at the ``elf_entry`` variable)

{% highlight c %}
static int load_elf_binary(struct linux_binprm *bprm)
{
    ...
	struct {
		struct elfhdr elf_ex;
		struct elfhdr interp_elf_ex;
	} *loc;
    ...
	/* Get the exec-header */
	loc->elf_ex = *((struct elfhdr *)bprm->buf);
    ...
	for (i = 0; i < loc->elf_ex.e_phnum; i++) {
		if (elf_ppnt->p_type == PT_INTERP) {
            ...
            
			elf_interpreter = kmalloc(elf_ppnt->p_filesz,
						  GFP_KERNEL);
            ...
			interpreter = open_exec(elf_interpreter);
            ...
            }
            ...
        }

    ...

	/* Do this so that we can load the interpreter, if need be.  We will
	   change some of these later */
	retval = setup_arg_pages(bprm, randomize_stack_top(STACK_TOP),       [1]
				 executable_stack);
    ...
	/* Now we do a little grungy work by mmapping the ELF image into
	   the correct location in memory. */
	for(i = 0, elf_ppnt = elf_phdata;
	    i < loc->elf_ex.e_phnum; i++, elf_ppnt++) {
		int elf_prot = 0, elf_flags, elf_fixed = MAP_FIXED_NOREPLACE;
		unsigned long k, vaddr;
		unsigned long total_size = 0;

		if (elf_ppnt->p_type != PT_LOAD)
			continue;
            ...
	}
    ...
	if (elf_interpreter) {
		unsigned long interp_map_addr = 0;

		elf_entry = load_elf_interp(&loc->interp_elf_ex,
					    interpreter,
					    &interp_map_addr,
					    load_bias, interp_elf_phdata);
		if (!IS_ERR((void *)elf_entry)) {
			/*
			 * load_elf_interp() returns relocation
			 * adjustment
			 */
			interp_load_addr = elf_entry;
			elf_entry += loc->interp_elf_ex.e_entry;
        }
	} else {
		elf_entry = loc->elf_ex.e_entry;
        ...
    }
    ...
#ifdef ARCH_HAS_SETUP_ADDITIONAL_PAGES
	retval = arch_setup_additional_pages(bprm, !!elf_interpreter);       [2]
	if (retval < 0)
		goto out;
#endif /* ARCH_HAS_SETUP_ADDITIONAL_PAGES */

	retval = create_elf_tables(bprm, &loc->elf_ex,                       [3]
			  load_addr, interp_load_addr);
    ...
	start_thread(regs, elf_entry, bprm->p);
    ...
}
{% endhighlight %}

A little note about three particular functions that appear:

 - ``setup_arg_pages()``(``[1]``): put into the stack ``argc``, ``argv`` and the environment variables
 (pratically the way the kernel communicates with the process)
 - ``arch_setup_additional_pages()`` (``[2]``): create the virtual gate for the syscall (the virtual library named ``linux-vdso.so.1``)
 - ``create_elf_tables()`` (``[3]``): put the **auxiliary vector** information in the stack just after the previous;
 this is the data that the kernel communicates to the loader

At this point the execution flow switches from the kernel, high privileged code, to user-land where the loader
will try to resolve the libraries and symbols.

## Symbols

Before we pass to analyze the loader and its code, we need to take a little more
about the segment with type ``PT_DYNAMIC``: it contains an array of elements
described using the following data type

```
typedef struct{
    Elf32_Sword d_tag;
    union{
        Elf32_Word d_val;
        Elf32_Addr d_ptr;
    } d_un;
} Elf32_Dyn;

externElf32_Dyn _DYNAMIC[]
```


| Type | Description |
|------|-------------|
| ``DT_NULL``       | |
| ``DT_NEEDED``     | This element holds the string table offset of a null-terminated string, giving the name of a needed library. The offset is an index into the table recorded in the ``DT_STRTAB`` entry |
| ``DT_STRTAB``     | This element holds the address of the string table. Symbol names, library names, and other strings reside in this table. |
| ``DT_SYMTAB``     | This element holds the address of the symbol table |
| ``DT_INIT``       | |
| ``DT_FINI``       | |
| ``DT_INIT_ARRAY`` | |
| ``DT_FINI_ARRAY`` | |

```
typedef struct {
    Elf64_Word st_name;
    unsigned char st_info;
    unsigned char st_other;
    Elf64_Half st_shndx;
    Elf64_Addr st_value;
    Elf64_Xword st_size;
} Efl64_Sym;
```

| Name | Description |
|------|-------------|
| ``st_name``  | index inside the corresponding string table |
| ``st_info``  | symbol bind and type attributes |
| ``st_other`` | symbol visibility |
| ``st_shndx`` | section this symbol refers to |
| ``st_value`` | can indicate a section offset (``ET_REL``) or a virtual address (``ET_EXEC``/``ET_DYN``) |
| ``st_size``  | symbol's size |

### Loader's code path

The code is for the ``glibc`` but obviously they exist other loaders; in a Debian
system is possible to obtain the source code with ``apt-get source glib-source``.

Consider that some part of the code must be implemented with the final architecture
in mind!

``struct link_map`` has a few different definitions

```
/* Structure describing a loaded shared object.  The `l_next' and `l_prev'
   members form a chain of all the shared objects loaded at startup.

   These data structures exist in space used by the run-time dynamic linker;
   modifying them may have disastrous results.

   This data structure might change in future, if necessary.  User-level
   programs must avoid defining objects of this type.  */

struct link_map
  {
    /* These first few members are part of the protocol with the debugger.
       This is the same format used in SVR4.  */

    ElfW(Addr) l_addr;		/* Difference between the address in the ELF
				   file and the addresses in memory.  */
    char *l_name;		/* Absolute file name object was found in.  */
    ElfW(Dyn) *l_ld;		/* Dynamic section of the shared object.  */
    struct link_map *l_next, *l_prev; /* Chain of loaded objects.  */

    /* All following members are internal to the dynamic linker.
       They may change without notice.  */

    /* This is an element which is only ever different from a pointer to
       the very same copy of this type for ld.so when it is used in more
       than one namespace.  */
    struct link_map *l_real;

    /* Number of the namespace this link map belongs to.  */
    Lmid_t l_ns;

    struct libname_list *l_libname;
    /* Indexed pointers to dynamic section.
       [0,DT_NUM) are indexed by the processor-independent tags.
       [DT_NUM,DT_NUM+DT_THISPROCNUM) are indexed by the tag minus DT_LOPROC.
       [DT_NUM+DT_THISPROCNUM,DT_NUM+DT_THISPROCNUM+DT_VERSIONTAGNUM) are
       indexed by DT_VERSIONTAGIDX(tagvalue).
       [DT_NUM+DT_THISPROCNUM+DT_VERSIONTAGNUM,
	DT_NUM+DT_THISPROCNUM+DT_VERSIONTAGNUM+DT_EXTRANUM) are indexed by
       DT_EXTRATAGIDX(tagvalue).
       [DT_NUM+DT_THISPROCNUM+DT_VERSIONTAGNUM+DT_EXTRANUM,
	DT_NUM+DT_THISPROCNUM+DT_VERSIONTAGNUM+DT_EXTRANUM+DT_VALNUM) are
       indexed by DT_VALTAGIDX(tagvalue) and
       [DT_NUM+DT_THISPROCNUM+DT_VERSIONTAGNUM+DT_EXTRANUM+DT_VALNUM,
	DT_NUM+DT_THISPROCNUM+DT_VERSIONTAGNUM+DT_EXTRANUM+DT_VALNUM+DT_ADDRNUM)
       are indexed by DT_ADDRTAGIDX(tagvalue), see <elf.h>.  */

    ElfW(Dyn) *l_info[DT_NUM + DT_THISPROCNUM + DT_VERSIONTAGNUM
		      + DT_EXTRANUM + DT_VALNUM + DT_ADDRNUM];
    const ElfW(Phdr) *l_phdr;	/* Pointer to program header table in core.  */
    ElfW(Addr) l_entry;		/* Entry point location.  */
    ElfW(Half) l_phnum;		/* Number of program header entries.  */
    ElfW(Half) l_ldnum;		/* Number of dynamic segment entries.  */

    /* Array of DT_NEEDED dependencies and their dependencies, in
       dependency order for symbol lookup (with and without
       duplicates).  There is no entry before the dependencies have
       been loaded.  */
    struct r_scope_elem l_searchlist;

    /* We need a special searchlist to process objects marked with
       DT_SYMBOLIC.  */
    struct r_scope_elem l_symbolic_searchlist;

    /* Dependent object that first caused this object to be loaded.  */
    struct link_map *l_loader;
    ...

    enum			/* Where this object came from.  */
      {
	lt_executable,		/* The main executable program.  */
	lt_library,		/* Library needed by main executable.  */
	lt_loaded		/* Extra run-time loaded shared object.  */
      } l_type:2;
      ...
    /* Start and finish of memory map for this object.  l_map_start
       need not be the same as l_addr.  */
    ElfW(Addr) l_map_start, l_map_end;
    /* End of the executable part of the mapping.  */
    ElfW(Addr) l_text_end;
    ...
    /* List of object in order of the init and fini calls.  */
    struct link_map **l_initfini;

    /* List of the dependencies introduced through symbol binding.  */
    struct link_map_reldeps
      {
	unsigned int act;
	struct link_map *list[];
      } *l_reldeps;
    unsigned int l_reldepsmax;

    /* Nonzero if the DSO is used.  */
    unsigned int l_used;
    ...
```

The ``GL(something)`` is a macro to access the fields into a global structure named ``struct rtld_global``
that you can find at ``sysdeps/generic/ldsodefs.h``.

```c
/* This is a list of all the modes the dynamic loader can be in.  */
enum mode { normal, list, verify, trace };
...
static void
dl_main (const ElfW(Phdr) *phdr,
	 ElfW(Word) phnum,
	 ElfW(Addr) *user_entry,
	 ElfW(auxv_t) *auxv)
{
    ...

  if (*user_entry == (ElfW(Addr)) ENTRY_POINT)
    {
      /* Ho ho.  We are not the program interpreter!  We are the program
	 itself!  This means someone ran ld.so as a command.  Well, that
	 might be convenient to do sometimes.  We support it by
	 interpreting the args like this:

	 ld.so PROGRAM ARGS...

     ...

    }
  else
    {
      /* Create a link_map for the executable itself.
	 This will be what dlopen on "" returns.  */
      main_map = _dl_new_object ((char *) "", "", lt_executable, NULL,
				 __RTLD_OPENEXEC, LM_ID_BASE);
      assert (main_map != NULL);
      main_map->l_phdr = phdr;
      main_map->l_phnum = phnum;
      main_map->l_entry = *user_entry;
      ...
    }
  ...

  /* Scan the program header table for the dynamic section.  */
  for (ph = phdr; ph < &phdr[phnum]; ++ph)
    switch (ph->p_type)
      {
      case PT_PHDR:
	/* Find out the load address.  */
	main_map->l_addr = (ElfW(Addr)) phdr - ph->p_vaddr;
	break;
      case PT_DYNAMIC:
	/* This tells us where to find the dynamic section,
	   which tells us everything we need to do.  */
	main_map->l_ld = (void *) main_map->l_addr + ph->p_vaddr;
	break;
    ...
      }
  /* Load all the libraries specified by DT_NEEDED entries.  If LD_PRELOAD
     specified some libraries to load, these are inserted before the actual
     dependencies in the executable's searchlist for symbol resolution.  */
  ...
  _dl_map_object_deps (main_map, preloads, npreloads, mode == trace, 0);
  ...
}
```

```
void
_dl_map_object_deps (struct link_map *map,
		     struct link_map **preloads, unsigned int npreloads,
		     int trace_mode, int open_mode)
{
  ...
  for (runp = known; runp; )
    {
    ...
      if (l->l_info[DT_NEEDED] || l->l_info[AUXTAG] || l->l_info[FILTERTAG])
	{
        ...
	  for (d = l->l_ld; d->d_tag != DT_NULL; ++d)
	    if (__builtin_expect (d->d_tag, DT_NEEDED) == DT_NEEDED)
	      {
		/* Map in the needed object.  */
		struct link_map *dep;

		/* Recognize DSTs.  */
		name = expand_dst (l, strtab + d->d_un.d_val, 0);
		/* Store the tag in the argument structure.  */
		args.name = name;

		int err = _dl_catch_exception (&exception, openaux, &args);
        ...
}
```

``elf/dl-load.c``

```
static void
openaux (void *a)
{
  struct openaux_args *args = (struct openaux_args *) a;

  args->aux = _dl_map_object (args->map, args->name,
			      (args->map->l_type == lt_executable
			       ? lt_library : args->map->l_type),
			      args->trace_mode, args->open_mode,
			      args->map->l_ns);
}
```

```
/* Map in the shared object file NAME.  */

struct link_map *
_dl_map_object (struct link_map *loader, const char *name,
		int type, int trace_mode, int mode, Lmid_t nsid)
{
  ...
  <this code deals with the library search path>
  ...
  void *stack_end = __libc_stack_end;
  return _dl_map_object_from_fd (name, origname, fd, &fb, realname, loader,
				 type, mode, &stack_end, nsid);
}
```

``elf/dl-load.c``

```

struct link_map *
_dl_map_object_from_fd (const char *name, const char *origname, int fd,
			struct filebuf *fbp, char *realname,
			struct link_map *loader, int l_type, int mode,
			void **stack_endp, Lmid_t nsid)
{
  ...
  /* Print debugging message.  */
  if (__glibc_unlikely (GLRO(dl_debug_mask) & DL_DEBUG_FILES))
    _dl_debug_printf ("file=%s [%lu];  generating link map\n", name, nsid);

  /* This is the ELF header.  We read it in `open_verify'.  */
  header = (void *) fbp->buf;
  ...
  /* Extract the remaining details we need from the ELF header
     and then read in the program header table.  */
  l->l_entry = header->e_entry;
  type = header->e_type;
  l->l_phnum = header->e_phnum;

  maplength = header->e_phnum * sizeof (ElfW(Phdr));
  if (header->e_phoff + maplength <= (size_t) fbp->len)
    phdr = (void *) (fbp->buf + header->e_phoff);
  else
    {
      phdr = alloca (maplength);
      ...
    }
  ...
  {
    /* Scan the program header table, collecting its load commands.  */
    ...
    for (ph = phdr; ph < &phdr[l->l_phnum]; ++ph)
      switch (ph->p_type)
	{
        ...
	}

    ...

    /* Now process the load commands and map segments into memory.
       This is responsible for filling in:
       l_map_start, l_map_end, l_addr, l_contiguous, l_text_end, l_phdr
     */
    errstring = _dl_map_segments (l, fd, header, type, loadcmds, nloadcmds,
				  maplength, has_holes, loader);
    ...
  }
  ...
}
```

and here we are at the end of the loading of the libraries, now we need to
load the objects

```c
/* Search loaded objects' symbol tables for a definition of the symbol
   UNDEF_NAME, perhaps with a requested version for the symbol.

   We must never have calls to the audit functions inside this function
   or in any function which gets called.  If this would happen the audit
   code might create a thread which can throw off all the scope locking.  */
lookup_t
_dl_lookup_symbol_x (const char *undef_name, struct link_map *undef_map,
		     const ElfW(Sym) **ref,
		     struct r_scope_elem *symbol_scope[],
		     const struct r_found_version *version,
		     int type_class, int flags, struct link_map *skip_map)
{
  ...
  struct r_scope_elem **scope = symbol_scope;
  ...
  /* Search the relevant loaded objects for a definition.  */
  for (size_t start = i; *scope != NULL; start = 0, ++scope)
    {
      int res = do_lookup_x (undef_name, new_hash, &old_hash, *ref,
			     &current_value, *scope, start, version, flags,
			     skip_map, type_class, undef_map);
      if (res > 0)
	break;
    ...
}


/* Inner part of the lookup functions.  We return a value > 0 if we
   found the symbol, the value 0 if nothing is found and < 0 if
   something bad happened.  */
static int
__attribute_noinline__
do_lookup_x (const char *undef_name, uint_fast32_t new_hash,
	     unsigned long int *old_hash, const ElfW(Sym) *ref,
	     struct sym_val *result, struct r_scope_elem *scope, size_t i,
	     const struct r_found_version *const version, int flags,
	     struct link_map *skip, int type_class, struct link_map *undef_map)
{
  size_t n = scope->r_nlist;
  ...
  struct link_map **list = scope->r_list;
  do
    {
      const struct link_map *map = list[i]->l_real;
      ...
      /* Print some debugging info if wanted.  */
      if (__glibc_unlikely (GLRO(dl_debug_mask) & DL_DEBUG_SYMBOLS))
	_dl_debug_printf ("symbol=%s;  lookup in file=%s [%lu]\n",
			  undef_name, DSO_FILENAME (map->l_name),
			  map->l_ns);
    ....
			sym = check_match (undef_name, ref, version, flags,        [1]
					   type_class, &symtab[symidx], symidx,
					   strtab, map, &versioned_sym,
					   &num_versions);
			if (sym != NULL)
			  goto found_it;
              ...
    }
  while (++i < n);
}
```

``[1]`` is the real symbol retrieving implementation (the complete code is wrapped
around the hash table related indexing).

``elf/dl-runtime.c``

```
/* This function is called through a special trampoline from the PLT the
   first time each PLT entry is called.  We must perform the relocation
   specified in the PLT of the given shared object, and return the resolved
   function address to the trampoline, which will restart the original call
   to that address.  Future calls will bounce directly from the PLT to the
   function.  */

DL_FIXUP_VALUE_TYPE
attribute_hidden __attribute ((noinline)) ARCH_FIXUP_ATTRIBUTE
_dl_fixup (
# ifdef ELF_MACHINE_RUNTIME_FIXUP_ARGS
	   ELF_MACHINE_RUNTIME_FIXUP_ARGS,
# endif
	   struct link_map *l, ElfW(Word) reloc_arg)
{
}
void
_dl_relocate_object (struct link_map *l, struct r_scope_elem *scope[],
		     int reloc_mode, int consider_profiling)
{
}
/* Set up the loaded object described by L so its unrelocated PLT
   entries will jump to the on-demand fixup code in dl-runtime.c.  */

static inline int __attribute__ ((unused, always_inline))
elf_machine_runtime_setup (struct link_map *l, int lazy, int profile)
{
  Elf64_Addr *got;
  ...
  if (l->l_info[DT_JMPREL] && lazy)
    {
      /* The GOT entries for functions in the PLT have not yet been filled
	 in.  Their initial contents will arrange when called to push an
	 offset into the .rel.plt section, push _GLOBAL_OFFSET_TABLE_[1],
	 and then jump to _GLOBAL_OFFSET_TABLE_[2].  */
      got = (Elf64_Addr *) D_PTR (l, l_info[DT_PLTGOT]);
      /* If a library is prelinked but we have to relocate anyway,
	 we have to be able to undo the prelinking of .got.plt.
	 The prelinker saved us here address of .plt + 0x16.  */
      if (got[1])
	{
	  l->l_mach.plt = got[1] + l->l_addr;
	  l->l_mach.gotplt = (ElfW(Addr)) &got[3];
	}
      /* Identify this shared object.  */
      *(ElfW(Addr) *) (got + 1) = (ElfW(Addr)) l;

      /* The got[2] entry contains the address of a function which gets
	 called to get the address of a so far unresolved function and
	 jump to it.  The profiling extension of the dynamic linker allows
	 to intercept the calls to collect information.  In this case we
	 don't store the address in the GOT so that all future calls also
	 end in this function.  */
      if (__glibc_unlikely (profile))
	{
       ...
	}
      else
	{
	  /* This function will get called to fix up the GOT entry
	     indicated by the offset on the stack, and then jump to
	     the resolved address.  */
	  if (GLRO(dl_x86_cpu_features).xsave_state_size != 0)
	    *(ElfW(Addr) *) (got + 2)
	      = (HAS_ARCH_FEATURE (XSAVEC_Usable)
		 ? (ElfW(Addr)) &_dl_runtime_resolve_xsavec
		 : (ElfW(Addr)) &_dl_runtime_resolve_xsave);
	  else
	    *(ElfW(Addr) *) (got + 2)
	      = (ElfW(Addr)) &_dl_runtime_resolve_fxsave;
	}
    }
}
```

By the way, if you want to see the trace of the process just described
you can use the ``LD_DEBUG`` environment variable to set the loader
in debug mode

```
$ LD_DEBUG=libs,bindings,files,symbols id
     14911:     
     14911:     WARNING: Unsupported flag value(s) of 0x8000000 in DT_FLAGS_1.
     14911:     
     14911:     file=libselinux.so.1 [0];  needed by id [0]
     14911:     find library=libselinux.so.1 [0]; searching
     14911:      search cache=/etc/ld.so.cache
     14911:       trying file=/lib/x86_64-linux-gnu/libselinux.so.1
     14911:     
     14911:     file=libselinux.so.1 [0];  generating link map
     14911:       dynamic: 0x00007f875d1d2d30  base: 0x00007f875cfae000   size: 0x0000000000227ab0
     14911:         entry: 0x00007f875cfb4b40  phdr: 0x00007f875cfae040  phnum:                  8
     14911:     
     14911:     
     14911:     file=libc.so.6 [0];  needed by id [0]
     14911:     find library=libc.so.6 [0]; searching
     14911:      search cache=/etc/ld.so.cache
     14911:       trying file=/lib/x86_64-linux-gnu/libc.so.6
     14911:     
     14911:     file=libc.so.6 [0];  generating link map
     14911:       dynamic: 0x00007f875cfa7b80  base: 0x00007f875cded000   size: 0x00000000001c0800
     14911:         entry: 0x00007f875ce111b0  phdr: 0x00007f875cded040  phnum:                 12
     14911:     
     14911:     
     14911:     file=libpcre.so.3 [0];  needed by /lib/x86_64-linux-gnu/libselinux.so.1 [0]
     14911:     find library=libpcre.so.3 [0]; searching
     14911:      search cache=/etc/ld.so.cache
     14911:       trying file=/lib/x86_64-linux-gnu/libpcre.so.3
     ...
     14911:     symbol=_res;  lookup in file=id [0]
     14911:     symbol=_res;  lookup in file=/lib/x86_64-linux-gnu/libselinux.so.1 [0]
     14911:     symbol=_res;  lookup in file=/lib/x86_64-linux-gnu/libc.so.6 [0]
     14911:     binding file /lib/x86_64-linux-gnu/libc.so.6 [0] to /lib/x86_64-linux-gnu/libc.so.6 [0]: normal symbol `_res' [GLIBC_2.2.5]
     ...
     14911:     symbol=_ITM_registerTMCloneTable;  lookup in file=id [0]
     14911:     symbol=_ITM_registerTMCloneTable;  lookup in file=/lib/x86_64-linux-gnu/libselinux.so.1 [0]
     14911:     symbol=_ITM_registerTMCloneTable;  lookup in file=/lib/x86_64-linux-gnu/libc.so.6 [0]
     14911:     symbol=_ITM_registerTMCloneTable;  lookup in file=/lib/x86_64-linux-gnu/libpcre.so.3 [0]
     14911:     symbol=_ITM_registerTMCloneTable;  lookup in file=/lib/x86_64-linux-gnu/libdl.so.2 [0]
     14911:     symbol=_ITM_registerTMCloneTable;  lookup in file=/lib64/ld-linux-x86-64.so.2 [0]
     14911:     symbol=_ITM_registerTMCloneTable;  lookup in file=/lib/x86_64-linux-gnu/libpthread.so.0 [0]
```

If you want to use a debugger and see live what happens, the real cool trick is to use the ``starti``
command inside ``gdb``: it stops at the first instruction after the kernel ``exec``, i.e. in the loader!

### Runtime relocations

Once the loader has completed its job and all the segments are mapped and the execution
is passed to the executable something remains to do.

```
$ objdump -j .plt -d public/code/simplest_excalation 

public/code/simplest_excalation:     formato del file elf32-i386


Disassemblamento della sezione .plt:

08049030 <.plt>:
 8049030:       ff 35 04 c0 04 08       pushl  0x804c004
 8049036:       ff 25 08 c0 04 08       jmp    *0x804c008
 804903c:       00 00                   add    %al,(%eax)
        ...

08049040 <printf@plt>:
 8049040:       ff 25 0c c0 04 08       jmp    *0x804c00c
 8049046:       68 00 00 00 00          push   $0x0
 804904b:       e9 e0 ff ff ff          jmp    8049030 <.plt>

08049050 <gets@plt>:
 8049050:       ff 25 10 c0 04 08       jmp    *0x804c010
 8049056:       68 08 00 00 00          push   $0x8
 804905b:       e9 d0 ff ff ff          jmp    8049030 <.plt>

08049060 <__libc_start_main@plt>:
 8049060:       ff 25 14 c0 04 08       jmp    *0x804c014
 8049066:       68 10 00 00 00          push   $0x10
 804906b:       e9 c0 ff ff ff          jmp    8049030 <.plt>

08049070 <putchar@plt>:
 8049070:       ff 25 18 c0 04 08       jmp    *0x804c018
 8049076:       68 18 00 00 00          push   $0x18
 804907b:       e9 b0 ff ff ff          jmp    8049030 <.plt>
$ objdump -j .got.plt -d public/code/simplest_excalation

public/code/simplest_excalation:     formato del file elf32-i386


Disassemblamento della sezione .got.plt:

0804c000 <_GLOBAL_OFFSET_TABLE_>:
 804c000:       14 bf 04 08 00 00 00 00 00 00 00 00 46 90 04 08     ............F...
 804c010:       56 90 04 08 66 90 04 08 76 90 04 08                 V...f...v...
```

As you can see the scheme is the following (take in mind that the entry point
is the ``whatever@plt`` label)

```
.plt:
   pushl GOT + 4
   jmp *(GOT + 8) i.e. loader

...

whatever@plt:
    jmp *(GOT + index)
    push index
    jmp .plt
...
```

## Format representation



## Further links

 - [System V ABIs](https://wiki.osdev.org/System_V_ABI)
 - [The ELF format - how programs look from the inside](https://greek0.net/elf.html)
 - [Vendor-specific ELF Note Elements](https://www.netbsd.org/docs/kernel/elf-notes.html)
 - [ELFkickers](https://github.com/BR903/ELFkickers): a collection of programs that access and manipulate ELF files
 - [Howto write shared libraries](https://akkadia.org/drepper/dsohowto.pdf)
 - http://www.phrack.org/archives/issues/58/4.txt
 - http://www.phrack.org/archives/issues/67/13.txt
 - https://davidad.github.io/blog/2014/02/19/relocatable-vs-position-independent-code-or/
 - http://netwinder.osuosl.org/users/p/patb/public_html/elf_relocs.html
 - [Linux gate](https://web.archive.org/web/20170128060623/http://www.trilithium.com/johan/2005/08/linux-gate/)
 - [System calls in the Linux kernel. Part 3](https://0xax.gitbooks.io/linux-insides/SysCall/linux-syscall-3.html)
 - [THE INSIDE STORY ON SHARED LIBRARIES AND DYNAMIC LOADING](https://www.dabeaz.com/papers/CiSE/c5090.pdf)
 - https://amir.rachum.com/blog/2016/09/17/shared-libraries/

