<!--
.. title: i comandi di git: for-each-ref
.. slug: i-comandi-di-git-for-each-ref
.. date: 2010-02-16 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Il mio strumento di versioning preferito è proprio ``git`` se non lo aveste
capito; la bellezza di questo tool sta proprio nella sua versatilità e nella
suo essere toolbox, una scatola degli attrezzi pronta all'uso per il versioning
dei propri progetti software. Con questo post inizio una carrellata sui comandi
di ``git``, magari più ignoti che potrebbero servirvi nel vostro lavoro di
sviluppo.

Il comando che andremo a vedere si chiama ``for-each-ref`` e già il nome può
darci indicazioni cosa si può ottenere da esso: una lista di tutto le referenze
del nostro repository, selezionando eventualmente un pattern particolare (solo
le tags per esempio).

Non c'è molto da spiegare se non vedere l'help presente

     $ git for-each-ref -h
     usage: git for-each-ref [options] [<pattern>]
    
        -s, --shell           quote placeholders suitably for shells
        -p, --perl            quote placeholders suitably for perl
        --python              quote placeholders suitably for python
        --tcl                 quote placeholders suitably for tcl
    
        --count <n>           show only <n> matched refs
        --format <format>     format to use for the output
        --sort <key>          field name to sort on

ed un possibile script di esempio che esegua, in un repository contenente un
progetto Django, gli unit tests per ognuno dei branch e ci stampi alla fine il
codice di uscita del test e la referenza a cui si riferisce, ordinandole per
risultato (attenzione che alla fine ci si ritrova con una detached ``HEAD``)

```bash
 git for-each-ref refs/heads | while read hash type ref
 do
     git checkout $hash 2>/dev/null
     python manage.py test >/dev/null 2>&1
     echo $ref $?
 done | sort -k2,2
```
Un output può essere il seguente

```
 refs/heads/backup 0
 refs/heads/fix-comma 0
 refs/heads/lighttpd 0
 refs/heads/make-tex-from-post 0
 refs/heads/archeology 1
 refs/heads/archives 1
 refs/heads/better-500-page 1
 refs/heads/export 2
```

Utile se si vuole tenere sott'occhio quali branch hanno bisogno di lavoro.

Un altro modo di utilizzare questo comando è di trovare a quale branch
corrisponde un dato commit: dentro uno script bash definite la sequente
funzione

```bash
 find_ref () {
     git for-each-ref refs/heads | while read sha1 type ref;
     do
         if [ "$sha1" == "$1" ]
         then
             echo $ref
         fi
      done
 }
```
a questo punto potete passare lo sha1 a 40 cifre a questa funzione e trovare il
path completo all'interno del namespace delle referenze a cui corrisponde
quella. Unico problema è che se ci sono più branch che puntano allo stesso
commit non c'è modo di disambiguarli.