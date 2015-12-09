---
layout: post
title: "i segreti degli script: redirezionare l'output"
comments: true
---
In un sistema ``UNIX``-like ogni applicazione ha come tre flussi di dati (detti
più tecnicamente *stream*) denominati **standard input**, **standard output** e
**standard error**, spesso indicati con termini più corti e tecnici ``stdin``,
``stdout`` e ``stderr``.

Ogni comando si comporta come una black box (ovviamente non i programmi aventi
una interfaccia grafica) che riceve degli input, li elabora e restituisce i
risultati, in caso di necessità aggiungendo delle informazioni aggiuntive
(errori, warnings etc...)

Per esempio per sapere quali partizioni occupano di più potete usare un insieme di comandi in cascata

    du -sh /* | sort -h -k1,1

e gustarvi l'ordinamento per scoprire in caso dove si trovano i file che occupano di più.

In particolare mi ero chiesto come potevo salvare l'output di uno script
all'occorrenza in un file nel caso, per esempio, in cui tramite accesso remoto
mi dovessi trovare ad usare ``screen(1)`` il quale non permette di scrollare il
terminale? Come sempre il codice altrui è l'esempio migliore da seguire ed in
particolare il codice di ``git``: lo script usato dalle routine di test
(consultabile in ``t/test-lib.sh``) ha un preambolo così strutturato

```bash
 # if --tee was passed, write the output not only to the terminal, but
 # additionally to the file test-results/$BASENAME.out, too.
 case "$GIT_TEST_TEE_STARTED, $* " in
 done,*)
	# do not redirect again
	;;
 *' --tee '*)
	mkdir -p test-results
	BASE=test-results/$(basename "$0" .sh)
	(GIT_TEST_TEE_STARTED=done ${SHELL-sh} "$0" "$@" 2>&1;
	 echo $? > $BASE.exit) | tee $BASE.out
	test "$(cat $BASE.exit)" = 0
	exit
	;;
 esac
```
in pratica il viene eseguito una istruzione molto simile allo ``switch`` in
``C``: viene controllata la stringa ``"$GIT_TEST_TEE_STARTED, $* "`` in caso
contenga la stringa ``done,*`` (dove ``*`` sta ad indicare una wildcard
rappresentante *qualsiasi cosa*) in tal caso significa che il flusso è già
stato rediretto, oppure controllare che sia stata passata l'opzione ``--tee``;
in tal caso, e l'idea geniale sta qui, viene impostata la variabile
``GIT_TEST_TEE_STARTED`` al valore ``done`` (in maniera da non eseguire il test
un'altra volta) e richiamato lo stesso script con gli stessi argomenti, ma
smistando l'output tramite ``tee(1)`` su un file avente il nome dello script
stesso (senza estensione ``.sh``).
