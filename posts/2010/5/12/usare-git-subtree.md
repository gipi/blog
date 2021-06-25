<!--
.. title: Usare git subtree
.. slug: usare-git-subtree
.. date: 2010-05-12 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Uno dei problemi della programmazione pratica è la modularizzazione del codice in maniera da poter essere condiviso fra vari progetti che possono usufruire della stessa base di funzionalità. Questo problema è condiviso anche per quanto riguarda il versioning di questo codice: come includere in un progetto il codice di una data libreria che esso utilizza? attraverso una installazione a parte oppure mantenendolo sotto la storia del progetto principale?

Tutti e due i casi hanno i loro pro e i loro contro, in entrambi i casi però si duplica la storia della libreria, rendendo difficoltoso includere nella storia ufficiale del progetto della stessa i cambiamenti che possono occorrere al codice per adattarlo alle funzionalità. Come strumento di versioning git mette a disposizione due strumenti per questo scopo: i **subtree** e i **submodule**.

In questo caso mi occuperò del primo strumento, sviluppato da Avery Pennarun (`blog <http://apenwarr.ca/log/>`_) che estende le funzionalità della strategia `subtree <http://www.kernel.org/pub/software/scm/git/docs/howto/using-merge-subtree.html>`_ per il merge, come descritto dal suo `post <http://apenwarr.ca/log/?m=200904#30>`_ da cui tutto ha avuto inizio.

Long story short: in pratica potete prendere la struttura DAG di un repository git e trapiantarlo in un altro progetto inserendolo in una apposita subdirectory, oppure all'inverso prendere una subdirectory ed estrarre la storia del codice ivi contenuto per andare a creare un nuovo repository. Qui di seguito le ricette veloci.

**Creare un nuovo progetto a partire da una subdirectory**

Supponiamo che abbiate in una sottodirectory chiamata ``huffman`` del codice da cui volete creare un nuovo repository: eseguendo il sottocomando ``split`` passando tramite l'opzione ``--prefix`` il path alla directory si ottiene l'hash della referenza che referenzia la nuova storia appena creata

.. code-block:: shell

 $ git subtree split --prefix=huffman
 78f0e2d39fffc2d56625b9b01e016054a91a7d44

Da questo è possibile trapiantare tramite una push.

**Unire un progetto**

Prima di tutto si necessita di aggiungere una referenza al repository esterno (``git remote add``) ed in seguito il download degli oggetti del database da questo (``git fetch``); una volta che questi sono presenti localmente è possibile richiamare ``subtree`` con il sotto-comando ``add``. Per riassumere ecco i comandi:

.. code-block:: shell

 $ git remote add jpeg /home/user/Programmazione/Ci/Jpeg/
 $ git fetch jpeg 
 warning: no common commits
 remote: Counting objects: 80, done.
 remote: Compressing objects: 100% (78/78), done.
 remote: Total 80 (delta 34), reused 0 (delta 0)
 Unpacking objects: 100% (80/80), done.
 From /home/user/Programmazione/Ci/Jpeg
  * [new branch]      master     -> jpeg/master
 $ git subtree add --prefix=jpeg remotes/jpeg/master
 Added dir 'jpeg'

e magicamente la directory ``jpeg/`` comparirà con tutta la storia riguardante quel progetto. La situzione che potete osservare alla fine del processo da ``gitk`` è la seguente

.. image:: http://ktln2.org/media//uploads/subtree-jpeg-import.jpg
 :align: center

cioé si è andato a creare un merge fra la storia importata (referenziata da ``remotes/jpeg/master``) e il branch ``master`` del progetto pre-esistente.

**Qualche parola in più**

Questo tool è possibile scaricarlo dal `repository <http://github.com/apenwarr/git-subtree>`_ presso `github <http://github.com/>`_ utilizzando il comando

.. code-block:: shell

 $ git clone git://github.com/apenwarr/git-subtree.git

L'installazione è abbastanza straightforward seguendo le istruzioni del file ``INSTALL``. Per completezza vi lascio con il menù di help

.. code-block:: shell

 $ git subtree
 usage: git subtree add   --prefix=<prefix> <commit>
    or: git subtree merge --prefix=<prefix> <commit>
    or: git subtree pull  --prefix=<prefix> <repository> <refspec...>
    or: git subtree push  --prefix=<prefix> <repository> <refspec...>
    or: git subtree split --prefix=<prefix> <commit...>

    -h, --help            show the help
    -q                    quiet
    -d                    show debug messages
    -P, --prefix ...      the name of the subdir to split out
    -m, --message ...     use the given message as the commit message for the merge commit

 options for 'split'
    --annotate ...        add a prefix to commit message of new commits
    -b, --branch ...      create a new branch from the split subtree
    --ignore-joins        ignore prior --rejoin commits
    --onto ...            try connecting new tree to an existing one
    --rejoin              merge the new branch back into HEAD

 options for 'add', 'merge', 'pull' and 'push'
    --squash              merge subtree changes as a single commit

e con il link a questo `tutorial <http://psionides.jogger.pl/2010/02/04/sharing-code-between-projects-with-git-subtree/>`_ dove sono indicate le diverse strategie possibili con questo comando (**squash** e **merge**) ed è presente anche qualche indicazione più particolareggiata, principalmente come aggiornare la subdirectory/progetto principale una volta che siano presenti cambiamenti.