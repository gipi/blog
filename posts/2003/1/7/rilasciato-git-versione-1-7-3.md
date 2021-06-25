<!--
.. title: Rilasciato GIT versione 1.7.3
.. slug: rilasciato-git-versione-1-7-3
.. date: 2003-01-07 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Piccolo annuncio: `Junio Hamano <http://gitster.livejournal.com/47628.html>`_ ha rilasciato ieri la nuova versione stabile di Git. Fra i tanti cambiamenti mi sento di segnalare questi due:

  * "git rebase --strategy <s>" learned "-X" option to pass extra options that are understood by the chosen merge strategy.

  * "git rebase -i" learned "exec" that you can insert into the insn sheet to run a command between its steps.

In particolare questo ultima novità nel comando rebase è molto interessante: come descritto dalla `patch iniziale <http://article.gmane.org/gmane.comp.version-control.git/152084>`_ permette di far lanciare un comando dalla directory radice del repository ad un certo punto del rebase; se il comando fallisce il rebase viene fermato in maniera da mettere mano ed è possibile continuare con il consueto ``git rebase --continue``. Una specie di ``bisect`` al contrario.

Per l'elenco delle novità e dei fixes vi rimando `all'annuncio nella mailing list <http://article.gmane.org/gmane.comp.version-control.git/156481>`_
