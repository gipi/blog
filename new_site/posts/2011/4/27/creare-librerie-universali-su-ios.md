<!--
.. title: creare librerie universali su IOS
.. slug: creare-librerie-universali-su-ios
.. date: 2011-04-27 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Se si utilizza una libreria statica in un proprio progetto XCode ovviamente si deve avere questa compilata sia per architettura ARM che per architettura i386 per riuscire ad usare  l'eseguibile sia su un device reale che sul simulatore. Difficilmente però la libreria verrà fornita in queste condizioni e quindi ci tocca utilizzare uno strumento presente nel sistema, il comando ``lipo(1)``: supponiamo di avere disponibili i due file di libreria per le due architetture chiamati ``libdummyARM.a`` e ``libdummyi386.a`` e di voler creare un file ``libdummy.a`` contenente entrambi, il comando da eseguire è

.. code-block:: bash

 $ lipo -create libdummyARM.a libdummyi386.a -output libdummy.a

per sicurezza è possibile controllare tramite il comando ``file(1)``

.. code-block:: bash

 $ file libdummy.a
 libdummy.a: Mach-O universal binary with 3 architectures
 libdummy.a (for architecture i386):	current ar archive random library
 libdummy.a (for architecture armv6):	current ar archive random library
 libdummy.a (for architecture armv7):	current ar archive random library

A questo punto basta includere ``libdummy.a`` in XCode ed il gioco è fatto.