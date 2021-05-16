<!--
.. title: natural key in Django
.. slug: natural-key-in-django
.. date: 2010-02-16 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Una delle cose non immediate con Django era scrivere delle fixtures i cui campi avessero dei riferimenti alla applicazione ``django.contrib.contenttypes``: siccome i valori di questa applicazione vengono generati al momento dell'esecuzione di ``syncdb`` succede che non è dato sapere, al momento della scrittura di una fixture, quale valore inserire in quel campo a meno di lanciare effettivamente ``syncdb`` oppure leggerlo dal database (sperando che il valore sia lo stesso).

Ma tutto questo è (quasi) un ricordo del passato: la versione 1.2 di Django (che è ancora una beta) `contiene una nuova funzionalità <http://docs.djangoproject.com/en/dev/releases/1.2-alpha-1/#natural-keys-in-fixtures>`_  chiamata `natural key <http://docs.djangoproject.com/en/dev/topics/serialization/#natural-keys>`_; con questa è possibile indicare nei campi di una fixture i valori attraverso cui riferirsi ad un oggetto.

Per capirci, in questo blog io utilizzo l'applicazione ``django-trackback`` e per alcuni test che vengono eseguiti, necessito di una fixture contenente una istanza di un modello di questa applicazione, la quale dovendo linkare una istanza di un modello di una applicazione qualsiasi, contiene un campo ``content_type``; per il discorso fatto appena sopra non posso sapere a priori che valore inserirci e anche se lo sapessi potrebbe non essere lo stesso del database usato dal sito di produzione (...oh yeah...). Per ovviare a questo posso usare appunto la seguente fixture

.. code-block:: json
 
  [
   {
     "pk": 2,
     "model": "trackback.trackback",
     "fields": {
       "title": "an awesome blog post",
       "url": "http://www.example-bis.com",
       "excerpt": "this guy rocks with his programming skill",
       "site": 1,
       "object_id": 1,
       "submit_date": "2010-02-12 09:45:29",
       "content_type": ["yadb", "blog"],
       "is_public": false,
       "remote_ip": "127.0.0.1",
       "blog_name": "Awesome Blog"
     }
   }
 ]

Come potete notare, il campo ``content_type`` contiene la lista ``["yadb", "blog"]``, questo perché il modello ContentType ha il suo manager che implementa la funzione ``get_by_natural_key`` che si occupa di risolvere il nome dell'applicazione (nel mio caso ``yadb``) e del modello (nel mio caso ``blog``); questo è il pezzo di codice originale in ``django/contrib/contenttypes/models.py``

.. code-block:: python

 class ContentTypeManager(models.Manager):

    ...

    def get_by_natural_key(self, app_label, model):
        try:
            ct = self.__class__._cache[self.db][(app_label, model)]
        except KeyError:
            ct = self.get(app_label=app_label, model=model)
        return ct

     ...

Ripeto che bisogna usare almeno l'alpha di Django-1.2 ma ne vale la pena.