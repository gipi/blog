<!--
.. title: pillole di PHP: loggare
.. slug: pillole-di-php-loggare
.. date: 2011-01-02 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Supponiamo di avere una classe ``PHP`` con una funzionalità di logging implementata tramite la classe Log di `PEAR <http://pear.php.net>`_ (installabile con #pear install log). Utilizzando massicciamente la funzionalità di log ci si può ritrovare (soprattutto nel caso il codice non sia stato scritto da noi stessi) a dover cercare nel sorgente quale riga ha generato una detererminata entrata nel file di log relativo; sarebbe comodo poter ottenere con poco sforzo l'indicazione della riga e della funzione in cui è stata chiamata per avere un immediato feedback di cosa stiamo osservando. Tutto questo è possibile utilizzando un pizzico di reflection del linguaggio PHP, evitando così di riempire di ``__LINE__`` e ``__FILE__`` espliciti i messaggi di log.

Per ottenere questo utilizzerò la funzione `debug_stacktrace() <http://it.php.net/manual/en/function.debug-backtrace.php>`_ che permette di ottenere in un array lo stack delle funzioni che hanno chiamato quella corrente assieme ad alcune informazioni come numero di linea, file etc...

Supponiamo di avere la seguente classe, con nella variabile privata ``$log`` una istanza singleton della classe ``Log``; chiamando il metodo ``log_info()`` è possibile andare ad inserire una entrata nel file di log

.. code-block:: php

 <?

 require_once("Log.php");

 class Dummy {
	private $log;

	public function __construct() {
		$this->log = Log::singleton('file', '/tmp/dummy.log');
	}

	private function log_info($msg) {
		$stack = debug_backtrace();
		$this->log->log(
			$stack[0]['file'].
			":".$stack[0]['line']
			.":".
			$stack[1]['function']."(): ".$msg, LOG_INFO);
	}

	public function doImportantStuff() {
                ...
		$this->log_info("loggiamo something of awesome");
                ...
	}
 }

 $dummy = new Dummy();
 $dummy->doImportantStuff();

Eseguendo questo snippet di codice ottengo nel file ``/tmp/dummy.log`` la seguente riga

.. code-block:: log

 Dec 27 19:02:46  [info] /tmp/logme.php:22:doImportantStuff(): loggiamo something of awesome