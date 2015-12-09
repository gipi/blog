---
layout: post
title: 'linux: come trovare i file di log di un demone'
comments: true
---
Per risolvere situazioni problematiche su una macchina è necessario per prima
cosa analizzare i log disponibili, ma in alcuni casi non si è sicuri quali
siano i file utilizzati.

Su Linux è possibile utilizzare gli strumenti messi a disposizione dal
filesystem virtuale ``/proc``: per esempio se vogliamo sapere quali file ha
aperto una istanza di apache2 possiamo usare la directory dei file descriptor
relativi al processo che ci interessa (in questo caso ``1909``)

     # tree -l /proc/1909/fd
     /proc/1909/fd
     ├── 0 -> /dev/null
     ├── 1 -> /dev/null
     ├── 2 -> /var/log/apache2/error.log
     ├── 3 -> socket:[1412228]
     ├── 4 -> socket:[1412229]
     ├── 5 -> pipe:[1412241]
     ├── 6 -> pipe:[1412241]
     ├── 7 -> /var/log/apache2/other_vhosts_access.log
     └── 8 -> /var/log/apache2/access.log

Così si scopre che lo ``stderr`` finisce in error log; per scoprire
effettivamente le caratteristiche dei socket e delle pipe è possibile fare una
ricerca più approfondita con il comando ``lsof(1)`` (di cui ne riporto solo una
porzione)

     # lsof -p 1909
     COMMAND  PID USER   FD   TYPE  DEVICE SIZE/OFF    NODE NAME
     ...
     apache2 1909 root    0r   CHR     1,3      0t0     550 /dev/null
     apache2 1909 root    1w   CHR     1,3      0t0     550 /dev/null
     apache2 1909 root    2w   REG     8,1      140 3164665 /var/log/apache2/error.log
     apache2 1909 root    3u  sock     0,6      0t0 1412228 can't identify protocol
     apache2 1909 root    4u  IPv6 1412229      0t0     TCP *:www (LISTEN)
     apache2 1909 root    5r  FIFO     0,8      0t0 1412241 pipe
     apache2 1909 root    6w  FIFO     0,8      0t0 1412241 pipe
     apache2 1909 root    7w   REG     8,1        0 3165100 /var/log/apache2/other_vhosts_access.log
     apache2 1909 root    8w   REG     8,1        0 3164641 /var/log/apache2/access.log

Sfortunatamente questo non esaurisce tutte le possibilità: il demone che si
occupa dei log di sistema è ``syslog`` (oppure ``rsyslog``) e viene chiamato
solo quando si necessita e quindi non risulta un socket/file collegato da
``apache2`` ad esso; per scoprire se effettivamente lo chiama è possibile fare
una analisi statica del binario molto grezza

     # nm -D `which apache2` | grep log
             U __syslog_chk
     ...
              U openlog

``openlog(3)`` è proprio la chiamata per aprire una connessione al logger di sistema.
