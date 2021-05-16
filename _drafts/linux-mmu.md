---
layout: post
comments: true
title: "How Linux handle memory"
tags: [WIP, low level, linux, mmu]
---

 - https://blog.twitter.com/engineering/en_us/topics/open-source/2021/dropping-cache-didnt-drop-cache.html
 - https://drgn.readthedocs.io/

A very important aspect in an operating system is the way the memory is handled,
both as a developer, security researcher; it's important to understand how the
system manages to provide memory from the software point of view (kernel-space
and user-space) but also from the hardware point of view.

## Hardware

For the CPU memory is as simple as putting an address on the bus and obtaining
in a couple of cycles a value in the same bus(?); if you want a real operating
system with process separation you would like to have a way to "swap" memory
between processes but in a complete transparent way so to not have to write code
in the application for that.

This is accomplished via the ``MMU``, i.e. the **M**emory **M**anagement
**U**nit, a piece of hardware that **translates** a **virtual address** to a
**physical address**.

https://wiki.osdev.org/MMU

A synonimous to MMU is the ``TLB`` **T**ranslation **L**ookaside **B**uffer

Obviously every architecture has its own way to do that but usually you have
some registers or memory locations where you put the address of some data
structure pointing to the description of the translation that you want for your
process. It's the operating system job to configure it each time he needs to
change the active process (this mechanism is called **context switch**).

## Software

Before looking at the code I need to explain the data structures used by the
Linux kernel to abstract away the underlying mechanism performed by hardware.

First of all we have two main address spaces, the so called **kernel space**,
where the "bytes" of the operating system are living and are usually
unaccessible by low permissions processes, and the **user space** where normal
user processes live with (usually) lower permissions than the kernel itself.

The more common configuration for Linux is to have, for process, a fixed size
address space (4GB for 32bit architecture) with a split 3:1 for user/kernel
space (for 32bit architectures we have 1GB reserved for the kernel and 3GB for
the user processes) where the higher part is associated with the operating
system. The split is determined by the variable named ``TASK_SIZE``


```
  ------------------- 2^32 or 2^64


        kernel


  ------------------- TASK_SIZE








       userspace







  ------------------- 0x0000...00
```

Note that this split is completely unrelated on how much physical RAM is
actually available: the address space is what is possible to address in
**theory**, it depends from the actual process instance how much of that address
space is actually referencing something "real".

It's important to note that in case of a context switch the kernel address space
doesn't need updating since it's fixed for all the processes; not
all operating systems behave in the same way, Linux itself could be configured
in a different way(?), and a complete split could be proficient from a security
point of view but obviously there are performance aspects the play a role here.

The bootloader loads the kernel binary at the **physical address** pointed by
``PHYSICAL_START``; this value depends from the specifics of the device you are
working with. The kernel at this point configures "the memory" so to access
directly the physical memory using an offset: the virtual address in which is
loaded is determined by ``PAGE_OFFSET``.

### Paging

``PAGE_OFFSET`` indicates the number of bits available to store metadata, and in practice is proportional
to the size of a page.

``arch/<architecture code>/asm/pgtable.h`` contains the code to interact with the
paget tables

### Context switch

```c
// kernel/sched/core.c
/*
 * context_switch - switch to the new MM and the new thread's register state.
 */
static __always_inline struct rq *
context_switch(struct rq *rq, struct task_struct *prev,
	       struct task_struct *next, struct rq_flags *rf)
{
	prepare_task_switch(rq, prev, next);

	/*
	 * For paravirt, this is coupled with an exit in switch_to to
	 * combine the page table reload and the switch backend into
	 * one hypercall.
	 */
	arch_start_context_switch(prev);

	/*
	 * kernel -> kernel   lazy + transfer active
	 *   user -> kernel   lazy + mmgrab() active
	 *
	 * kernel ->   user   switch + mmdrop() active
	 *   user ->   user   switch
	 */
	if (!next->mm) {                                // to kernel
		enter_lazy_tlb(prev->active_mm, next);

		next->active_mm = prev->active_mm;
		if (prev->mm)                           // from user
			mmgrab(prev->active_mm);
		else
			prev->active_mm = NULL;
	} else {                                        // to user
		membarrier_switch_mm(rq, prev->active_mm, next->mm);
		/*
		 * sys_membarrier() requires an smp_mb() between setting
		 * rq->curr / membarrier_switch_mm() and returning to userspace.
		 *
		 * The below provides this either through switch_mm(), or in
		 * case 'prev->active_mm == next->mm' through
		 * finish_task_switch()'s mmdrop().
		 */
		switch_mm_irqs_off(prev->active_mm, next->mm, next);

		if (!prev->mm) {                        // from kernel
			/* will mmdrop() in finish_task_switch(). */
			rq->prev_mm = prev->active_mm;
			prev->active_mm = NULL;
		}
	}

	rq->clock_update_flags &= ~(RQCF_ACT_SKIP|RQCF_REQ_SKIP);

	prepare_lock_switch(rq, next, rf);

	/* Here we just switch the register state and the stack. */
	switch_to(prev, next, prev);
	barrier();

	return finish_task_switch(prev);
}
```

the core of the memory management is inside ``switch_mm_irqs_off()``

### Architecture specific code

#### x86

For the x86 architecture, the most documented if you are looking for operating
systems stuff, use the special register ``C3``

```c
// arch/x86/mm/tlb.c
void switch_mm_irqs_off(struct mm_struct *prev, struct mm_struct *next,
			struct task_struct *tsk)
{
	struct mm_struct *real_prev = this_cpu_read(cpu_tlbstate.loaded_mm);
	u16 prev_asid = this_cpu_read(cpu_tlbstate.loaded_mm_asid);
	bool was_lazy = this_cpu_read(cpu_tlbstate.is_lazy);
	unsigned cpu = smp_processor_id();
	u64 next_tlb_gen;
	bool need_flush;
	u16 new_asid;

    ...

	if (need_flush) {
		this_cpu_write(cpu_tlbstate.ctxs[new_asid].ctx_id, next->context.ctx_id);
		this_cpu_write(cpu_tlbstate.ctxs[new_asid].tlb_gen, next_tlb_gen);
		load_new_mm_cr3(next->pgd, new_asid, true);

		trace_tlb_flush(TLB_FLUSH_ON_TASK_SWITCH, TLB_FLUSH_ALL);
	} else {
		/* The new ASID is already up to date. */
		load_new_mm_cr3(next->pgd, new_asid, false);

		trace_tlb_flush(TLB_FLUSH_ON_TASK_SWITCH, 0);
	}

	/* Make sure we write CR3 before loaded_mm. */
	barrier();

    ...

    if (next != real_prev) {
		cr4_update_pce_mm(next);
		switch_ldt(real_prev, next);
	}
}
```

indeed the main functoon doing the job is ``load_new_mm_cr3()``.

 - http://www.maizure.org/projects/evolution_x86_context_switch_linux/

For the structure of the ``PTE`` you can look [here](https://wiki.osdev.org/Paging)
and you can see the flags at ``arch/x86/include/asm/pgtable_types.h``

#### ARM

There are two main different approach for the ``MMU`` in ``ARM`` cores, one via the ``CP15`` register, mainly
used with 32bit architectures and one with the ``TTBR0_EL1`` and ``TTBR1_EL1``
registers, used in 64bit architectures.

```
# ARM926T
config CPU_ARM926T
	bool
	select CPU_32v5
	select CPU_ABRT_EV5TJ
	select CPU_CACHE_VIVT
	select CPU_COPY_V4WB if MMU
	select CPU_CP15_MMU
	select CPU_PABRT_LEGACY
	select CPU_THUMB_CAPABLE
	select CPU_TLB_V4WBI if MMU
	help
	  This is a variant of the ARM920.  It has slightly different
	  instruction sequences for cache and TLB operations.  Curiously,
	  there is no documentation on it at the ARM corporate website.

	  Say Y if you want support for the ARM926T processor.
	  Otherwise, say N.
```

```asm
// arch/arm/mm/proc-arm922.S
/* =============================== PageTable ============================== */

/*
 * cpu_arm922_switch_mm(pgd)
 *
 * Set the translation base pointer to be as described by pgd.
 *
 * pgd: new page tables
 */
	.align	5
ENTRY(cpu_arm922_switch_mm)
#ifdef CONFIG_MMU
	mov	ip, #0
#ifdef CONFIG_CPU_DCACHE_WRITETHROUGH
	mcr	p15, 0, ip, c7, c6, 0		@ invalidate D cache
#else
@ && 'Clean & Invalidate whole DCache'
@ && Re-written to use Index Ops.
@ && Uses registers r1, r3 and ip

	mov	r1, #(CACHE_DSEGMENTS - 1) << 5	@ 4 segments
1:	orr	r3, r1, #(CACHE_DENTRIES - 1) << 26 @ 64 entries
2:	mcr	p15, 0, r3, c7, c14, 2		@ clean & invalidate D index
	subs	r3, r3, #1 << 26
	bcs	2b				@ entries 63 to 0
	subs	r1, r1, #1 << 5
	bcs	1b				@ segments 7 to 0
#endif
	mcr	p15, 0, ip, c7, c5, 0		@ invalidate I cache
	mcr	p15, 0, ip, c7, c10, 4		@ drain WB
	mcr	p15, 0, r0, c2, c0, 0		@ load page table pointer
	mcr	p15, 0, ip, c8, c7, 0		@ invalidate I & D TLBs
#endif
	ret	lr
```

 - [About the MMU for the ARM926EJ-S](https://developer.arm.com/documentation/ddi0198/e/memory-management-unit/about-the-mmu)
 - [ARM32 TTBR](https://developer.arm.com/documentation/ddi0198/e/programmer-s-model/register-descriptions/translation-table-base-register-c2?lang=en)
 - [Aarch64 Configuring and enabling the MMU](https://developer.arm.com/documentation/den0024/a/The-Memory-Management-Unit/Translating-a-Virtual-Address-to-a-Physical-Address/Configuring-and-enabling-the-MMU)


```c
// arch/arm64/mm/context.c
void cpu_do_switch_mm(phys_addr_t pgd_phys, struct mm_struct *mm)
{
	unsigned long ttbr1 = read_sysreg(ttbr1_el1);
	unsigned long asid = ASID(mm);
	unsigned long ttbr0 = phys_to_ttbr(pgd_phys);

	/* Skip CNP for the reserved ASID */
	if (system_supports_cnp() && asid)
		ttbr0 |= TTBR_CNP_BIT;

	/* SW PAN needs a copy of the ASID in TTBR0 for entry */
	if (IS_ENABLED(CONFIG_ARM64_SW_TTBR0_PAN))
		ttbr0 |= FIELD_PREP(TTBR_ASID_MASK, asid);

	/* Set ASID in TTBR1 since TCR.A1 is set */
	ttbr1 &= ~TTBR_ASID_MASK;
	ttbr1 |= FIELD_PREP(TTBR_ASID_MASK, asid);

	write_sysreg(ttbr1, ttbr1_el1);
	isb();
	write_sysreg(ttbr0, ttbr0_el1);
	isb();
	post_ttbr_update_workaround();
}
```

#### SPARC V9

This is a particular architecture because with its MMU allows to provide a
context (I interpret as user/kernel-space) for a memory access allowing to have
complete separated address spaces.

```c
// arch/sparc/include/asm/mmu_context_64.h
/* Switch the current MM context. */
static inline void switch_mm(struct mm_struct *old_mm, struct mm_struct *mm, struct task_struct *tsk)
{
	unsigned long ctx_valid, flags;
	int cpu = smp_processor_id();

	per_cpu(per_cpu_secondary_mm, cpu) = mm;
	if (unlikely(mm == &init_mm))
		return;

	spin_lock_irqsave(&mm->context.lock, flags);
	ctx_valid = CTX_VALID(mm->context);
	if (!ctx_valid)
		get_new_mmu_context(mm);

	/* We have to be extremely careful here or else we will miss
	 * a TSB grow if we switch back and forth between a kernel
	 * thread and an address space which has it's TSB size increased
	 * on another processor.
	 *
	 * It is possible to play some games in order to optimize the
	 * switch, but the safest thing to do is to unconditionally
	 * perform the secondary context load and the TSB context switch.
	 *
	 * For reference the bad case is, for address space "A":
	 *
	 *		CPU 0			CPU 1
	 *	run address space A
	 *	set cpu0's bits in cpu_vm_mask
	 *	switch to kernel thread, borrow
	 *	address space A via entry_lazy_tlb
	 *					run address space A
	 *					set cpu1's bit in cpu_vm_mask
	 *					flush_tlb_pending()
	 *					reset cpu_vm_mask to just cpu1
	 *					TSB grow
	 *	run address space A
	 *	context was valid, so skip
	 *	TSB context switch
	 *
	 * At that point cpu0 continues to use a stale TSB, the one from
	 * before the TSB grow performed on cpu1.  cpu1 did not cross-call
	 * cpu0 to update it's TSB because at that point the cpu_vm_mask
	 * only had cpu1 set in it.
	 */
	tsb_context_switch_ctx(mm, CTX_HWBITS(mm->context));

	/* Any time a processor runs a context on an address space
	 * for the first time, we must flush that context out of the
	 * local TLB.
	 */
	if (!ctx_valid || !cpumask_test_cpu(cpu, mm_cpumask(mm))) {
		cpumask_set_cpu(cpu, mm_cpumask(mm));
		__flush_tlb_mm(CTX_HWBITS(mm->context),
			       SECONDARY_CONTEXT);
	}
	spin_unlock_irqrestore(&mm->context.lock, flags);
}
```

 - [The SPARC Architecture Manual](https://cr.yp.to/2005-590/sparcv9.pdf)

#### MIPS

The``PTE`` flags are defined at ``arch/mips/include/asm/pgtable-bits.h``

 - [MIPS architecture for programmers Vol. III: MIPS32® / microMIPS32™ Privileged Resource Architecture](https://s3-eu-west-1.amazonaws.com/downloads-mips/documents/MD00090-2B-MIPS32PRA-AFP-06.02.pdf) pg 57 has PTE format
