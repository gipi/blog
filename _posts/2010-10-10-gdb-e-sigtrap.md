---
layout: post
title: 'GDB e SIGTRAP'
comments: true
---
Mi sono ritrovato a debuggare al lavoro una applicazione IPhone che crashava
senza però lasciarmi con la console di ``gdb`` in modo da ottenere un
backtrace.

Lavorandoci sopra sono arrivato alla conclusione che l'applicazione riceveva un
segnale di ``SIGTRAP``, segnale che viene usato dai debugger stessi per i loro
breakpoints: nel caso specifico ,una libreria interna del SDK, "emetteva"
questo segnale confondendo così il debugger che non si fermava in maniera
corretta.

Per correggere questo problema basta indicare a ``gdb`` di "inoltrare il
segnale" all'applicazione in maniera tale da in effetti ottenere poi un
terminale del debugger funzionante; per fare ciò basta impostare un breakpoint
ad inizio dell'applicazione (per andare sul sicuro magari nel ``main()``) e poi
dare il comando

    (gdb) handle SIGTRAP pass
    (gdb) c

e per magia vi ritrovete appunto con la linea di comando di ``gdb`` al prossimo crash.

Per saperne di più al riguardo di come gestire i segnali con ``gdb`` questo è il suo relativo help

    (gdb) help handle
    Specify how to handle a signal.
    Args are signals and actions to apply to those signals.
    Symbolic signals (e.g. SIGSEGV) are recommended but numeric signals
    from 1-15 are allowed for compatibility with old versions of GDB.
    Numeric ranges may be specified with the form LOW-HIGH (e.g. 1-5).
    The special arg "all" is recognized to mean all signals except those
    used by the debugger, typically SIGTRAP and SIGINT.
    Recognized actions include "stop", "nostop", "print", "noprint",
    "pass", "nopass", "ignore", or "noignore".
    Stop means reenter debugger if this signal happens (implies print).
    Print means print a message if this signal happens.
    Pass means let program see this signal; otherwise program doesn't know.
    Ignore is a synonym for nopass and noignore is a synonym for pass.
    Pass and Stop may be combined.


