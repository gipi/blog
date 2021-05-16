<!--
.. title: eseguire testing di una applicazione web dalla command line
.. slug: eseguire-testing-di-una-applicazione-web-dalla-command-line
.. date: 2010-05-10 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Certe volte è necessario eseguire dei tests su una applicazione web, come per esempio controllare che effettivamente il login funzioni, che le pagine siano validabili o anche quanti accessi sono consentiti prima che inizi a dare problemi (una specie di crash test); questa interfaccia di testing in alcuni framework (per esempio `Django <http://djangoproject.com>`_) è inclusa in essi ed è percio facilmente utilizzabile, ma come fare per progetti non appartenenti a queste categorie?

Una soluzione è l'uso di ``curl``, uno *spider* da linea di comando che permette di eseguire azioni "da browser" comodamente senza interfaccia grafica e in maniera automatizzata. Partiamo dalle basi senza nessun impegno di completezza, in quanto una analisi esauriente riguardante l'utilizzo di questo strumento richiederebbe un post a parte.

Il più semplice utilizzo è di ottenere il contenuto di una determinata URL

.. code-block:: shell

 $ curl http://dominio/page.html

Nel caso in cui il server esegua una redirect, questo comando non restituisce nulla ed è perciò consigliabile aggiungere l'opzione ``--location`` che fa rieseguire la query sulla URL finale; in caso è possibile usare ``--head`` per ottenere **solo** gli headers e nel caso di redirezione stampa in successione gli header di tutte le pagine a cui esegue le richieste.

È possibile anche fare il submit di form

.. code-block:: shell

 curl --form "username=${USERNAME}" --form "password=${PASSWORD}" [URL]

La parte interessante consiste nella possibilità di poter immagazzinare/usare cookie tramite l'opzione ``-c``

.. code-block:: shell

 curl -c /tmp/google.cookie -A "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.2.1)" "http://www.google.it/search?q=lolcats"

e bellamente si ottiene in ``/tmp/google.cookie`` un file contenente le info che google ti lascia in the browser (l'opzione ``-A`` serve ad impostare lo ``User Agent`` cioé l'identificativo del client usato per la richiesta che in questo caso è necessario altrimenti bigG ti restituisce errore in quanto pensa che tu sia un bot malevolo).

**validazione**

Il consorzio web (il mitico W3C) ha un `servizio di validazione <http://validator.w3.org/>`_ con delle `API <http://validator.w3.org/docs/api.html>`_ pubbliche tramite cui è possibile per l'appunto controllare che le vostre pagine seguano gli standard: nel seguente esempio si effettua la validazione dell'homepage di questo sito richiedendo di stampare solo il riassunto che si ritrova negli header

.. code-block:: shell

 $ curl --head 'http://validator.w3.org/check?uri=http%3A%2F%2Fwww.ktln2.org&output=soap12'
 HTTP/1.1 200 OK
 Date: Mon, 10 May 2010 10:58:18 GMT
 Server: Apache/2.2.9 (Debian) mod_python/3.3.1 Python/2.5.2
 X-W3C-Validator-Recursion: 1
 X-W3C-Validator-Status: Invalid
 X-W3C-Validator-Errors: 15
 X-W3C-Validator-Warnings: 1
 Content-Type: application/soap+xml; charset=UTF-8

**Pingkback**

Anche il cosidetto `pingback <http://www.hixie.ch/specs/pingback/pingback>`_ deve essere testato in qualche maniera e pensare di farlo manualmente è da malati di mente; seguendo le specifiche proprie di questa variante dell'xml-rpc si possono utilizzare le seguenti righe: questo è il file ``debug_trackback.xml``

.. code-block:: xml

 <?xml version="1.0"?>
 <methodCall>
	<methodName>pingback.ping</methodName>
	<params>
		<param>
			<value>
				<string>http://www.example.com</string>
			</value>
		</param>
		<param>
			<value>
				<string>http://localhost:8000/post/miao</string>
			</value>
		</param>
	</params>
 </methodCall>

da utilizzare sempre con ``curl``

.. code-block:: shell

 $ curl -H "Content-Type: application/xml" -X POST --data-binary  \
     @debug_trackback.xml http://localhost:8000/blog/pingback/xml-rpc/
 <?xml version='1.0'?>
 <methodResponse>
 <params>
 <param>
 <value><string>OK</string></value>
 </param>
 </params>
 </methodResponse>