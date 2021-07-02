<!--
.. title: linux: breve tutorial sull'initrd
.. slug: linux-breve-tutorial-sullinitrd
.. date: 2012-03-25 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

**Initrd** è l'abbreviazione di **init** ial **r** am **d** isk, cioè un
filesystem da tenere in ``RAM`` usato da un sistema linux per effettuare un
boot completo.

Per capire il suo utilizzo bisogna prima fare una premessa: un kernel linux è
di tipo (semi-)monolitico, in pratica i driver per le periferiche sono interni
al kernel stesso: quindi per avere un kernel `generale` che funzioni su più
hardware possibile dovremmo compilarlo inserendo tutti i driver disponibili ma
facendo così renderemmo il kernel stesso molto pesante. Ci viene in aiuto il
fatto che questo OS non è completamente monolitico ma predispone la possibilità
di compilare i propri device driver anche come **moduli**, cioè come delle
speciali librerie da attivare al momento più opportuno tramite i comandi in
user space come ``modprobe``.

Il problema è in parte risolto, in realtà solo spostato: i moduli sono file e
come tutti i file saranno presenti su un filesystem che per essere
opportunamente gestito dal kernel dovrà avere il necessario driver (sia per il
filesystem che per il controller ``SATA`` che per quello ``PCI``) caricato;
proprio per evitare questo si utilizza un `early userspace`, cioè un filesystem
con tutti i moduli possibili da cui il kernel potrà caricare solo quelli
necessari.

Per capire effettivamente come funziona nel dettaglio è meglio fare una
carrellata dei passaggi che linux esegue all'avvio:

 1. il booloader carica il kernel e l'initrd
 2. il kernel converte initrd in un normale disco ``RAM`` e libera la memoria prima occupata da questo
 3. se non indicato diversamente viene usata come root device ``/dev/ram0`` che corrisponde proprio ad initrd
 4. /init viene eseguito (a meno che non si passi l'opzione ``rdinit`` con un eseguibile alternativo)
 5. init deve preoccuparsi di effettuare il mount del vero root file system utilizzando la chiamata di sistema ``pivot_root``
 6. a questo punto init cerca /sbin/init nel nuovo filesystem e lo esegue completando la procedura di boot

Ovviamente nulla vieta di creare un initrd che semplicemente esegue una shell:
per esempio esiste la versione del [net-installer di Debian per ARM](http://d-i.debian.org/daily-images/armel/daily/versatile/netboot/) che in
qualche mega di ``initrd`` ha tutto quello che serve per riuscire ad installare
un sistema funzionante su questa architettura.

È possibile utilizzare due tipologie di initrd

 - un semplice archivio compresso
 - un vero e proprio filesystem

mi occuperò solamente del primo caso in quanto è molto più semplice. L'archivio compresso è del tipo gestito dal comando ``cpio(1)`` e possiamo averne un esempio prendendo un initrd che probabilmente esiste già nel vostro sistema nella directory ``boot``.

    $ mkdir initrd && cd initrd
    $ cat /boot/initrd.gz | gunzip | cpio -imd
    52109 blocks
    $ ls
    bin  conf  etc  init  lib  run  sbin  scripts

come potete vedere dall'ultimo comando sono disponibili tutte le directory che
ci aspetterebbe in un sistema. Inversamente per ricreare un initrd a partire
dal contenuto di una directory basta eseguire

    find . | cpio -H newc -o | gzip -n -9 > new-initrd.gz

Ma come crearsi un proprio `early userspace`? È disponibile nei sorgenti del
kernel linux un comando predisposto a questo scopo chiamato ``gen_init_cpio``
nella directory ``usr/``. Quello che segue è l'help

     $ usr/gen_init_cpio 
     Usage:
        usr/gen_init_cpio [-t <timestamp>] <cpio_list>

     <cpio_list> is a file containing newline separated entries that
     describe the files to be included in the initramfs archive:

     # a comment
     file <name> <location> <mode> <uid> <gid> [<hard links>]
     dir <name> <mode> <uid> <gid>
     nod <name> <mode> <uid> <gid> <dev_type> <maj> <min>
     slink <name> <target> <mode> <uid> <gid>
     pipe <name> <mode> <uid> <gid>
     sock <name> <mode> <uid> <gid>
    
     <name>       name of the file/dir/nod/etc in the archive
     <location>   location of the file in the current filesystem
                  expands shell variables quoted with ${}
     <target>     link target
     <mode>       mode/permissions of the file
     <uid>        user id (0=root)
     <gid>        group id (0=root)
     <dev_type>   device type (b=block, c=character)
     <maj>        major number of nod
     <min>        minor number of nod
     <hard links> space separated list of other links to file
    
     example:
     # A simple initramfs
     dir /dev 0755 0 0
     nod /dev/console 0600 0 0 c 5 1
     dir /root 0700 0 0
     dir /sbin 0755 0 0
     file /sbin/kinit /usr/src/klibc/kinit/kinit 0755 0 0
    
     <timestamp> is time in seconds since Epoch that will be used
     as mtime for symlinks, special files and directories. The default
     is to use the current time for these entries.

Nel mio caso specifico ho utilizzato questi file

     $ cat cpio.conf 
     # A simple initramfs
     dir /dev 0755 0 0
     nod /dev/console 0600 0 0 c 5 1
     dir /root 0700 0 0
     dir /sbin 0755 0 0
     dir /bin 0755 0 0
     file /init /pandora/raspberrypi/init-debian-arm.sh 0755 0 0
     file /sbin/busybox /opt/busybox/busybox 0755 0 0
     slink /bin/sh /sbin/busybox 0755 0 0
     slink /sbin/chroot /sbin/busybox 0755 0 0
     slink /sbin/mount /sbin/busybox 0755 0 0
     slink /bin/mkdir /sbin/busybox 0755 0 0
     slink /bin/ls /sbin/busybox 0755 0 0
     $ cat init-debian-arm.sh 
     #!/bin/sh
    
     echo "Loading, please wait..."
    
     [ -d /dev ] || mkdir -m 0755 /dev
     [ -d /root ] || mkdir -m 0700 /root
     [ -d /sys ] || mkdir /sys
     [ -d /proc ] || mkdir /proc
     [ -d /tmp ] || mkdir /tmp
     mkdir -p /var/lock
     mount -t sysfs -o nodev,noexec,nosuid sysfs /sys
     mount -t proc -o nodev,noexec,nosuid proc /proc
    
     # Note that this only becomes /dev on the real filesystem if udev's scripts
     # are used; which they will be, but it's worth pointing out
     tmpfs_size="10M"
     if [ -e /etc/udev/udev.conf ]; then
        . /etc/udev/udev.conf
     fi
     if ! mount -t devtmpfs -o mode=0755 udev /dev; then
        echo "W: devtmpfs not available, falling back to tmpfs for /dev"
        mount -t tmpfs -o size=$tmpfs_size,mode=0755 udev /dev
        [ -e /dev/console ] || mknod -m 0600 /dev/console c 5 1
        [ -e /dev/null ] || mknod /dev/null c 1 3
     fi
     mkdir /dev/pts
     mount -t devpts -o noexec,nosuid,gid=5,mode=0620 devpts /dev/pts || true
     mount -t tmpfs -o "nosuid,size=20%,mode=0755" tmpfs /run
    
     ls /dev
    
     rootmnt=/root
     init=/sbin/init
    
     mount -t ext4 /dev/sda ${rootmnt}
    
     # Chain to real filesystem
     exec chroot ${rootmnt} ${init} <${rootmnt}/dev/console >${rootmnt}/dev/console
     echo "Could not execute run-init."

(questo ultimo è il nostro ``init`` `ispirato` da quello presente nel sistema
Debian che ha hardcodato il fatto che la root è ``/dev/sda`` e il device ha un
filesystem ``ext4``) e ho generato l'archivio con il comando

    $ /usr/src/linux-2.6/usr/gen_init_cpio cpio.conf | gzip -9 -n > new-initrd.gz

Da tenere conto che siccome l'initrd deve avere delle funzionalità di base non
è necessario utilizzare le glibc ma il più delle volte si preferisce la
leggerezza di librerie alternative come per esempio [busybox](http://busybox.net/) che in un unico eseguibile (compilato staticamente)
mette a disposizione tutti i maggiori comandi ``*NIX``.

Per provare effettivamente l'initrd così generato è possibile utilizzare qemu


    $ qemu-system-i386 -kernel bzImage -initrd new-initrd.gz -hda hd.img

e se tutto va bene dovreste vedere la procedura di boot avvenire correttamente.

Ovviamente se volete saperne di più vi consiglio di leggervi i file nei
sorgenti di linux, in particolare
``Documentation/filesystems/ramfs-rootfs-initramfs.txt`` e
``Documentation/initrd.txt``.