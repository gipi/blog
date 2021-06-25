<!--
.. title: user mode linux
.. slug: user-mode-linux
.. date: 2011-10-31 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Una delle problematiche sentite da chi sviluppa in ambito enterprise e non è la necessità di testare correttamente alcune configurazioni di sistema avendo a disposizione un ambiente pulito; esistono molte possibilità per fare questo tra cui la virtualizzazione tramite strumenti quali VirtualBox, WMWare e simili, una possibilità sconosciuta ai più è l'utilizzo di Linux in user space tramite ``user mode linux`` (per gli amici ``UML``).

Il vantaggio di UML è la semplicità di avere una instanza di linux su terminale con cui poter effettuare i test ed in caso avere la stessa istanza "pulita" al prossimo riavvio.

Prima di tutto recuperiamo una versione: è possibile farlo dal sito http://user-mode-linux.sourceforge.net oppure in un sistema Debian dal pacchetto ``user-mode-linux``. Partiamo usando la versione sul sito ufficiale e scarichiamo il `kernel <http://user-mode-linux.sourceforge.net/linux-2.6.24-rc7.bz2>`_ e decomprimiamolo; ci ritroveremo con un eseguibile capace di lanciare un kernel 2.6.24 in user space. Quello che ci manca è il filesystem con un sistema installato: è possibile scaricare anche quello dal sito che però è un sistema Fedora mentre nei miei esempi successivi userò una mia immagine con una installazione Debian.

**Attenzione:** ogni cambiamento apportato all'interno del filesystem sarà permanente a meno di non  usare il meccanismo della `Copy On Write <http://en.wikipedia.org/wiki/Copy_on_write>`_, cioè indicando prima del file contenente il filesystem un file in cui scrivere i cambiamenti; i due vanno separati con una virgola o con i due punti.

.. code-block:: text

 $ ./linux-2.6.24-rc7 ubd0=copy-on-write.cow,Debian-5.0-x86-root_fs

Dopo il primo avvio è possibile indicare in quelli successivi solamente il file COW, infatti esso è capace di andare a recuperare l'immagine disco originale. In alcune situazioni può capitare che nell'utilizzo della COW ci sia qualche problema: se vi si presente un errore di questo tipo all'avvio (probabilmente nascosto nei log di avvio)

.. code-block:: text

 mtime mismatch (1308387691 vs 1317491141) of COW header vs backing file
 Failed to open 'mycow.cow', errno = 22

significa che il modification time dei due file non corrisponde: se sapete che non ci sono problemi potete riallinearli usando il seguente comando

.. code-block:: text

 $ LANG=en mtime=1308387691;touch --date="`date -d 1970-01-01\ UTC\ $mtime\ seconds`" /2Hd/UML/Debian-5.0-x86-root_fs

NETWORKING
----------------

Ovviamente l'emulazione non sarebbe completa senza un irrinunciabile connessione di rete: per abilitare il networking è sufficiente aggiungere la seguente opzione all'avvio

.. code-block:: text

 eth0=tuntap,,,192.168.0.254

ed una volta avviata la macchina, da dentro di essa eseguire

.. code-block:: text

 # ifconfig eth0 192.168.0.5 up
 * modprobe tun
 * ifconfig tap0 192.168.0.254 netmask 255.255.255.255 up
 * bash -c echo 1 > /proc/sys/net/ipv4/ip_forward
 * route add -host 192.168.0.5 dev tap0
 * bash -c echo 1 > /proc/sys/net/ipv4/conf/tap0/proxy_arp
 * arp -Ds 192.168.0.5 eth0 pub
 # route add default gw 192.168.0.254

Ovviamente gli indirizzi IP scelti devono essere liberi nella sottorete in cui ci si trova.

Per evitare di perdere 1 ora come il sottoscritto, prima di tutto controllate di avere le uml_utilities `installate <http://user-mode-linux.sourceforge.net/minis.html#utils>`_ sull'host; per un sistema Debian like si può optare per la sequenza di comandi

.. code-block::

 # apt-get install uml-utilities
 # adduser gipi uml-net

dove bisogna sostituire ``gipi`` con l'utente che esegue uml.

UTILIZZARE FILE SUL SISTEMA HOST
-------------------------------------------

Un modo molto semplice per accedere ai file presenti sul sistema host è di montarlo
all'interno di UML: il seguente comando

.. code-block:: bash

 # mount none /host -t hostfs

effettua il mount della root dell'host nella directory ``/host`` in UML.


COMANDARE ISTANZE DI UML
-----------------------------------

È anche possibile comandare dall'esterno una istanza UML durante il suo funzionamento usando il comando ``uml_mconsole``: quando l'istanza si avvia in mezzo ai log è possibile riconoscere una riga del tipo

.. code-block:: text

 mconsole (version 2) initialized on /home/user/.uml/2qN27t/mconsole

Quello indicato è un file di tipo socket tramite cui impartire comandi (quelli disponibili li trovate alla pagina di manuale del comando). Se per esempio avviate una istanza ma dopo che il sistema si è avviato vi rendete conto che non vi ricordate la password di root è possibile eseguire l'halt della macchina con un semplice

.. code-block:: text

 $ uml_mconsole 2qN27t
 (2qN27t) halt
 OK


COMPILARLO DAI SORGENTI
---------------------------------

Ovviamente è possibile compilare la nostra versione di UML prendendo i sorgenti del kernel, entrando nella directory che li contiene e utilizzando le seguenti istruzioni (che sono poi le istruzioni standard per la compilazione di un kernel dai sorgenti)

.. code-block:: text

 $ make mrproper
 $ make mrproper ARCH=um
 $ make defconfig ARCH=um
 $ make menuconfig ARCH=um # qui scegliete il processore (non obbligatorio)
 $ make ARCH=um