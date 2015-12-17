---
layout: post
title: 'Debug una chiamata SOAP con netcat'
comments: true
---
Può succedere di dover debuggare una chiamata ad un servizio web esterno (nel
mio caso una chiamata SOAP) effettuata attraverso un wrapper PHP; può succedere
che la chiamata fallisca e il messaggio risulti veramente criptico e si
necessiti di dover avere accesso all'XML effettivamente scambiato fra lo script
e il server esterno, ma come fare?

Basta utilizzare ``ncat`` come
[proxy](http://nmap.org/ncat/guide/ncat-proxy.html) in locale con l'accortezza
di usarne un'altra istanza per ottenere effettivamente il flusso in input ed
output delle chiamate: se da un terminale si esegue

    $ ncat --sh-exec "tee /tmp/stdin.txt | ncat localhost 8080 | tee /tmp/stdout.txt" -l 8888 -vvv

si crea una socket bindato alla porta 8888 che reindirizza sempre in locale
alla porta 8080, scrivendo però su file ``stdin.txt`` e ``stdout.txt``
rispettivamente le richieste in entrata e quelle in uscita; sulla porta 8080
mettiamo in ascolto ``ncat`` in modalità proxy

    $ ncat -l 8080 --proxy-type http -vvvv

A questo punto impostando lo script ad usare come proxy ``localhost`` alla
porta 8888 posso ottenere il flusso di dati in entrata ed in uscita.

**Update:** Mi accorgo solo ora che è possibile usare una variabile ``trace``
con la quale poter farsi restituire l'XML inviato con le librerie [SOAP PHP](http://www.php.net/manual/en/soapclient.getlastresponse.php). Poco male,
qualcosa l'ho imparato lo stesso ;-).
