<!--
.. title: git: usare git bisect per un baco impossibile
.. slug: git-usare-git-bisect-per-un-baco-impossibile
.. date: 2011-07-17 00:00:00
.. tags: git
.. category: 
.. link: 
.. description: 
.. type: text
-->

Durante la risoluzione di un baco relativo ad una applicazione iphone mi sono
ritrovato con un problema molto strano: una UITableView contenuta all'interno
di una UIView con una UINavigationBar; sulla barra di navigazione è presente un
tasto per impostare le celle in modalità di editing (in particolare è possibile
cancellare le celle). Quando le celle sono in modalità di editing esse
presentano un tasto rosso circolare sulla sinistra, almeno è quello che doveva
e avveniva precedentemente: ora in modalità di editing non si presenta il tasto
circolare a sinistra ma un tasto normale a destra quando si scorre il dito
verso destra sulla cella in questione.
 

Questo baco è stato segnalato e io non me ne ero mai accorto, e qualche tempo
prima il tutto funzionava correttamente; la prima cosa da fare è stata
controllare che tra una versione funzionante e l'attuale non ci fossero delle
modifiche nel controller in questione ma non ce n'erano. Quindi per risolvere
il problema ho pensato bene di utilizzare uno strumento molto potente contenuto
in git: il comando **bisect**.

In pratica tramite esso è possibile effettuare una bisecazione fra coppie di
snapshot di codice caratterizzate dal contenere o meno il baco che si cerca di
risolvere: se il baco è stato introdotto in un particolare commit è possibile
trovarlo raffinando ad ogni passo l'intervallo da bisecare.

Per prima cosa si parte definendo la coppia di commit da cui iniziare: uno
*buono*, rappresentato dalla revisione indicata con la tag ``v2.0``, ed uno
*cattivo* che è l'attuale ``HEAD``:

    $ git bisect start
    $ git bisect bad
    $ git bisect good v2.0

A questo punto git effettuerà il checkout di un commit che si trova a metà fra
i due appena indicati; l'utente effettua i propri tests e deciderà se il commit
è buono

    $ git bisect good

oppure no

    $ git bisect bad

fino a che non rimane un solo commit per cui il nostro strumento di
versioning ci avvisa che è questo il commit che ha introdotto il baco

    4cc6e967075e75c5f9dca8798609c7f333d3e0f2 is the first bad commit
    commit 4cc6e967075e75c5f9dca8798609c7f333d3e0f2
    Author: Gianluca <gianluca@MBP-DFUN.local>
    Date:   Mon Apr 18 10:40:47 2011 +0200

    Add footer which is missing in some views.
    
    Because of this we have to reparent some table within a view and add manually
    the property tableView.

     :040000 040000 f2daebc6bf95879c91e7bc4dc24ad4baaa1dee74 625993b0272a9e0f18d98bd12ffdf1190b3d1213 M	LumBancoProva
     :040000 040000 eb48902995d470bace32c37837a7ac4ab61b0670 417f22a4e0121c7ce6947b764add79397932728d M	LumLib

In pratica il problema riscontrato era dovuto ad un reparenting della
UITableView dentro ad una UIView andando a non inviare il messaggio ``-
(void)setEditing:(BOOL)editing animated:(BOOL)animate`` alla table view ma alla
view.

Non immagino come avrei potuto risolvere diversamente questa spiacevole
regressione. Come ultima considerazione c'è da tenere conto che in caso di
processo automatizzato è possibile indicare a bisect uno script da utilizzare
per marcare i vari commit come *buoni* o *cattivi* rendendo il processo
immediato.