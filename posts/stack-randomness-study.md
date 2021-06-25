<!--
.. title: stack randomness study
.. slug: stack-randomness-study
.. date: 2021-06-06 13:22:28 UTC
.. tags: Linux,security
.. category: 
.. link: 
.. description: 
.. type: text
.. status: draft
.. has_math: true
-->

In the old post about [ELF format](/2019/10/28/elf/)

```c
static int load_elf_binary(struct linux_binprm *bprm)
{
   ...
	retval = setup_arg_pages(bprm, randomize_stack_top(STACK_TOP),
				 executable_stack);
   ...
```

[randomize_stack_top() at fs/binfmt_elf.c](https://elixir.bootlin.com/linux/v3.2/source/fs/binfmt_elf.c#L543)

```c
/* to align the pointer to the (next) page boundary */
#define PAGE_ALIGN(addr) ALIGN(addr, PAGE_SIZE)

#ifndef STACK_RND_MASK
#define STACK_RND_MASK (0x7ff >> (PAGE_SHIFT - 12))	/* 8MB of VA */
#endif

unsigned long randomize_stack_top(unsigned long stack_top)
{
	unsigned long random_variable = 0;

	if ((current->flags & PF_RANDOMIZE) &&
		!(current->personality & ADDR_NO_RANDOMIZE)) {
		random_variable = get_random_int() & STACK_RND_MASK;
		random_variable <<= PAGE_SHIFT;
	}

#ifdef CONFIG_STACK_GROWSUP
	return PAGE_ALIGN(stack_top) + random_variable;
#else
	return PAGE_ALIGN(stack_top) - random_variable;
#endif
}
```

This has the the effect of generating a 11-bit random offset to use starting from ``PAGE_SHIFT`` bits.

Having this value the kernel passes it to
[setup_arg_pages() at fs/exec.c](https://elixir.bootlin.com/linux/v3.2/source/fs/exec.c#L652)

```c
int setup_arg_pages(struct linux_binprm *bprm,
		    unsigned long stack_top,
		    int executable_stack)
{
	unsigned long ret;
	unsigned long stack_shift;
	struct mm_struct *mm = current->mm;
	struct vm_area_struct *vma = bprm->vma;
	struct vm_area_struct *prev = NULL;
	unsigned long vm_flags;
	unsigned long stack_base;
	unsigned long stack_size;
	unsigned long stack_expand;
	unsigned long rlim_stack;

	stack_top = arch_align_stack(stack_top);
	stack_top = PAGE_ALIGN(stack_top);

	if (unlikely(stack_top < mmap_min_addr) ||
	    unlikely(vma->vm_end - vma->vm_start >= stack_top - mmap_min_addr))
		return -ENOMEM;

	stack_shift = vma->vm_end - stack_top;

	bprm->p -= stack_shift;
	mm->arg_start = bprm->p;

	if (bprm->loader)
		bprm->loader -= stack_shift;
	bprm->exec -= stack_shift;

    ...

	/* Move stack pages down in memory. */
	if (stack_shift) {
		ret = shift_arg_pages(vma, stack_shift);
		if (ret)
			goto out_unlock;
	}

	/* mprotect_fixup is overkill to remove the temporary stack flags */
	vma->vm_flags &= ~VM_STACK_INCOMPLETE_SETUP;

	stack_expand = 131072UL; /* randomly 32*4k (or 2*64k) pages */
	stack_size = vma->vm_end - vma->vm_start;
	/*
	 * Align this down to a page boundary as expand_stack
	 * will align it up.
	 */
	rlim_stack = bprm->rlim_stack.rlim_cur & PAGE_MASK;
	if (stack_size + stack_expand > rlim_stack)
		stack_base = vma->vm_end - rlim_stack;
	else
		stack_base = vma->vm_start - stack_expand;
	current->mm->start_stack = bprm->p;
	ret = expand_stack(vma, stack_base);
	if (ret)
		ret = -EFAULT;

out_unlock:
	mmap_write_unlock(mm);
	return ret;
}
```

[arch_align_stack() at arch/x86/kernel/process.c](https://elixir.bootlin.com/linux/v3.2/source/arch/x86/kernel/process.c#L656)

```c
unsigned long arch_align_stack(unsigned long sp)
{
	if (!(current->personality & ADDR_NO_RANDOMIZE) && randomize_va_space)
		sp -= get_random_int() % 8192;
	return sp & ~0xf;
}
```

This generates a random 10-bit offset (8192 is 0x2000, i.e. 14-bit but the lowest 4-bit are discarded from the
end result).

The remaining ``PAGE_ALIGN`` macro enforces the alignment to the 4K boundary (12 bits), i.e. it removes another 8 bits
from the remaining 10 bits from ``arch_align_stack()``.

At the end we have

```

 |7|f|f|f|f|r|r|r|0|0|0|
```

https://mziccard.me/2015/05/08/modulo-and-division-vs-bitwise-operations/
