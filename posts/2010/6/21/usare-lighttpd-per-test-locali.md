<!--
.. title: Usare lighttpd per test locali
.. slug: usare-lighttpd-per-test-locali
.. date: 2010-06-21 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Durante lo sviluppo di qualche applicazione web based si può presentare la necessità di avere a disposizione un web server funzionante, vuoi perché si necessita di testare uno script ``PHP``, vuoi perché qualche applicazione a livello client deve testare delle funzionalità che richiedono la presenza esplicita di un nome di dominio (per esempio la funzionalità di `localStorage <https://developer.mozilla.org/en/DOM/Storage#localStorage>`_ su firefox che non funziona per una pagina caricata in locale, cioè con il protocollo ``file://``).

La prima opzione sarebbe usare apache che però in alcuni casi risulta come ammazzare una mosca con un cannone anche tenendo conto che le varie configurazioni necessitano i permessi di super utente (a meno di avere una installazione locale personalizzata); l'opzione più semplice è quella di utilizzare `lighttpd <http://www.lighttpd.net/>`_, un server web famoso per la sua leggerezza e per la sua facilità di configurazione. Una particolarità che mi indirizza verso la sua scelta è la possibilità di poter lanciare il suo demone senza avere accesso come superutente e poter richiamare nel file di configurazione alcune variabili d'ambiente importate dalla istanza del terminale da cui è lanciato.

Il seguente file di configurazione è quello che uso personalmente e tramite di esso è possibile configurare questo web server per ascoltare richieste alla porta 8000 rispondendo opportunamente a script ``CGI`` come eseguibili, script ``PHP`` e ``Perl`` assegnando correttamente i mimetype ai tipi di file più comuni.

.. code-block:: shell
 
 var.basedir = var.CWD
 # <http://www.madboa.com/geek/openssl/#cert>
 var.sslcertpath = env.HOME + "/.ssl-cert.pem"
 server.document-root = basedir
 server.port = 8000
 #server.errorlog = "/tmp/.lighttpd-error.log"
 debug.log-request-header = "enable"
 

 # http://redmine.lighttpd.net/wiki/1/Docs:ModDirlisting
 dir-listing.activate = "enable"

 mimetype.assign = (
   ".html" => "text/html", 
   ".txt" => "text/plain",
   ".jpg" => "image/jpeg",
   ".png" => "image/png",
   ".js" => "text/javascript"
 )
 
 server.modules = ("mod_cgi", "mod_accesslog")
 
 accesslog.filename = "/tmp/.lighttpd-access.log"
 
 # CGI is the way
 cgi.assign = (".cgi" => "",
               ".php" => "/usr/bin/php-cgi",
 	      ".pm"  => "/usr/bin/perl")

 # SSL <http://redmine.lighttpd.net/projects/lighttpd/wiki/Docs:SSL>
 $SERVER["socket"] == ":8080" {
	ssl.engine  = "enable"
	ssl.pemfile = var.sslcertpath
 }
 
Se inseriamo quanto scritto appena sopra in un file chiamato .lighttpd.conf è possibile richiamarlo da linea di comando tramite

.. code-block:: shell

 $ /usr/sbin/lighttpd -D -f ~/.lighttpd.conf
 2010-06-21 10:41:09: (log.c.166) server started

A questo punto si ha un webserver che utilizza come webroot la directory da cui è stato lanciato.
L'opzione ``-D`` evita che il demone vada in background, per chiuderlo usare il segnale ``SIGKILL`` usando ``Ctrl-C``.