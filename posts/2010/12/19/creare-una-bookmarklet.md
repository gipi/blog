<!--
.. title: Creare una bookmarklet
.. slug: creare-una-bookmarklet
.. date: 2010-12-19 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Attualmente il browser rappresenta l'applicativo più usato in moltissimi ambiti quotidiani e la sua personalizzazione può rappresentare una necessità ed una comodità; poi chi come sviluppatore vuole rendere un proprio applicativo web, un servizio, realmente fruibile dall'utenza ha spesso la necessità di rendere immediato l'utilizzo evitando copia/incolla fra pagine web. Proprio per questo motivo moltissimi servizi web mettono a disposizione delle funzionalità su altre pagine web tramite l'utilizzo di cosidette *bookmarklet*, cioé semplici bookmark che eseguono azioni, per esempio

  * `instapaper <http://instapaper.com>`_ fantastico servizio che permette di salvare pagine per essere rilette in seguito; crea in automatico una versione di testo così da poter leggere anche su apparecchi a bassa risoluzione.
  * `markup.io <http://markup.io>`_ una specie di `pastebin <http://pastebin.com>`_ per designer.

Creare una bookmarklet è molto semplice: si crea un bookmark (anche vuoto) e si inserisce nella locazione il seguente snippet di codice

.. code-block:: javascript

 javascript:alert('miao');

Andando su una qualunque pagina, cliccando la bookmarklet, si aprirà un alert con il testo "miao"; nulla di trascendentale ma sufficiente a mostrare il fatto che da una bookmarklet è possibile eseguire javascript nel contesto di una data pagina. Ovviamente è possibile eseguire codice più "raffinato", magari includendo una libreria javascript di propria preferenza per migliorare l'aspetto/funzionalità di una pagina.

Per esempio, per includere in una pagina la libreria `jQuery <http://jquery.com>`_

.. code-block:: javascript

 (function(){
   var head = document.getElementsByTagName('head')[0];
   var script = document.createElement('script');
   script.type='text/javascript';
   script.src="http://code.jquery.com/jquery-1.4.4.min.js";
   head.appendChild(script);
  })();

(avendo l'accortezza di eliminare spazi e newline). Per effettivamente programmare questi bookmarklet consiglio l'utilizzo della console di `firebug <http://getfirebug.com/>`_, che permette di lanciare javascript direttamente nella pagina prescelta con un'area di testo abbastanza ampia.

Linkografia
-----------

Per un esempio più interessante (aggiungere la possibilità di ordinare i dati dentro una tabella HTML, oppure visualizzare dei grafici a partire dai dati della stessa) potete leggervi il link seguente

  * http://www.latentmotion.com/how-to-create-a-jquery-bookmarklet/

L'approccio seguito è quello di creare un tag script il quale include uno script remoto che si preoccupa di eseguire una determinata azione al termine dell'evento "onload".