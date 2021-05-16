<!--
.. title: concatenare l'output di due comandi
.. slug: concatenare-loutput-di-due-comandi
.. date: 2011-05-30 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Se per qualche motivo si necessita di ottenere una stringa da due comandi di shell separati da mandare in input ad un terzo è possibile usare una subshell, instanziandola tramite il costrutto ``(..;..;..)``.

Nel seguente esempio mandiamo a ``comando3`` l'output di ``comando1`` giustapposto a quello di ``comando2``:


    $ (comando1 ; comando2) | comando3