<!--
.. title: creare un RadioButton senza immagine
.. slug: creare-un-radiobutton-senza-immagine
.. date: 2011-09-07 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

La soluzione è abbastanza banale solo che non è immediata, mi ci sono voluti vari tentativi: prima di tutto bisogna notare che esiste l'attributo di style ``android:button`` che prende una drawable in ingresso e la prima idea è stata quella di creare una immagine ``0x0``; funziona ma il problema è che mostra un quadratino minuscolo anti-estetico.

La soluzione definitiva è stata utilizzare una risorsa interna identificata nel namespace Java come ``android.R.id.empty``: nel file di layout è possibile indicarla tramite

.. code-block:: xml

 <RadioButton
   android:button="@android:id/empty"
 />

A questo punto ci si ritrova con un ``RadioButton`` senza nessuna immagine. Consigliabile di creare un insieme di stili per definire visivamente gli stati del bottone in questione, altrimenti potrebbe risultare inusabile.