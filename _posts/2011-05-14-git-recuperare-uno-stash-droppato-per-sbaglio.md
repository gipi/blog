---
layout: post
title: 'git: recuperare uno stash droppato per sbaglio'
comments: true
tags: [git]
---
Nel mio normale workflow uso spesso ``git stash`` assieme alla suite di tests eventualmente presenti nel progetto a cui lavoro, per assicurarmi che ad un commit non manchino parti funzionali utili; la procedura è la seguente (facendo finta che sia un progetto Django)

```
 $ git commit
 $ git stash
 $ python manage.py test
 $ git stash pop
```

Una volta però mi è successo di dare un drop di troppo andando a perdere lo stash appena salvato


    $ git stash drop
    Dropped refs/stash@{0} (2b1f538fc094df2a8391c7462ae6586995f3fef4)

fortuna vuola che fino a che non si esegue un ``git gc`` anche gli elementi non direttamente referenziati rimangano nel database degli oggetti del repository permettendone l'eventuale utilizzo; eseguendo

    $ git stash apply 2b1f538fc094df2a8391c7462ae6586995f3fef4

è possibile recuperare lo stash perduto.
