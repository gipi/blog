<!--
.. title: xcode cannot run using the selected device
.. slug: xcode-cannot-run-using-the-selected-device
.. date: 2011-05-25 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

L'errore che dà il titolo a questo post è il risultato del tentativo di compilare un progetto dopo l'aggiornamento a XCode4. Nella immagine di seguito potete vedere un esempio

.. image:: http://ktln2.org/media//uploads/error.png

Per risolvere il problema semplicemente potete controllare che XCode non abbia impostato la versione di iOS per il "Deployment target" ad essere superiore a quella del device. Per correggerla basta andare nella sezione indicata nella immagine qui sotto (non so come indicarla a parole visto che la nuova versione di questo IDE mi sembra un po' confusionaria, soprattutto provenendo dalla versione precedente)

.. image:: http://ktln2.org/media//uploads/deployment.png
  :align: center

La soluzione è tratta da `stack overflow <http://stackoverflow.com/questions/5984305/xcode-cannot-run-using-the-selected-device-error>`_