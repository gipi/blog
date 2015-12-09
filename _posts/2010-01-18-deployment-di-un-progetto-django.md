---
layout: post
title: 'Deployment di un progetto Django'
comments: true
---
Siccome Django è un framework **web** e siccome esso mette a disposizione degli
strumenti per il test locale, in un corretto modello di sviluppo e testing la
parte in cui i cambiamenti vengono resi noti al mondo esterno in un server
reale, rappresentano un passaggio importante e delicato; i passaggi devono
essere automatizzati in maniera tale da evitare di dimenticarli o compierli in
maniera errata (sopratutto se il sito in questione non è usato direttamente
dallo sviluppatore, il quale non può accorgersi di eventuali problemi anche
piccoli che possono presentarsi).

Possiamo dividere le buone pratiche per un *corretto deploy* (TM)
principalmente in due categorie: 

* accorgimenti da prendere quando si scrive il codice.
* strategia per il deploy/upgrade sul server.

Uno dei problemi più sentiti, che potenzialmente può essere molto lungo da
risolvere e, sopratutto, non prevedibili consiste nella gestione delle
dipendenze a cui è soggetta la tua web application, sopratutto nel caso in cui
essa conviva nello stesso shared hosting con altre che richiedono versioni
diverse delle librerie: per risolvere questo scenario sono possibili due vie
(nel caso in cui voi usiate un version manager software, ma voi lo usate
vero;-))

* salvare le dipendenze nel vostro SCM.
* usare una sandbox per le vostre librerie (per esempio virtualenv).

Io propendo per la seconda opzione siccome permette di lasciare più snello il
progetto, evitando di portarsi dietro MB di librerie (spesso in forma binaria)
che poi risulterebbe veramente difficile poter aggiornare se non sporcando
inevitabilmente la storia del vostro repository (nel caso in cui voi usiate un
version manager software, ma voi lo usate vero;-)). Ovviamente per lo stesso
motivo sarebbe inutile tenere sotto versioning la sandbox anche nell'ottica di
una automatizzazione: mica volete uno script che vi registri anche l'hosting in
automatico? certi passaggi vanno fatti bene e automatizzati ma, è questo il
punto importante, a parte e non assieme al deploy vero e proprio, magari con
tempistiche proprie e coerenti con il loro scopo.

## Impostazioni iniziali

Sempre nell'ottica della customizzabilità delle impostazioni della vostra web
application, è pratica giusta e buona inserire nel file settings.py le
impostazioni comuni con i settaggi più restrittivi ed usare un file
``local_settings.py`` da importare con le specifiche impostazioni per la
specifica installazione. Infatti una delle cose più fastidiose all'inizio è
dover cambiare tutte le variabili che impostano i percorsi, in alcuni casi
assoluti, che sicuramente cambieranno già solo nei momenti di debug in computer
usati per lo sviluppo; un esempio su tutti è la variabile ``TEMPLATE_DIRS``.

Quindi primo passo è creare una variabile che contenga il path del progetto nel nostro filesystem usando la keyword ``__file__``

```python
 PROJECT_ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
```

modifichiamo ``MEDIA_ROOT``, ``MEDIA_URL`` e ``ADMIN_MEDIA_PREFIX``

```python
 MEDIA_ROOT = PROJECT_ROOT_PATH + '/media/'
 MEDIA_URL = '/media/'
 ADMIN_MEDIA_PREFIX = '/admin_media/'
```

Cancelliamo dal file globale la ``SECRET_KEY`` e
[creiamone una nuova](http://blog.leosoto.com/2008/04/django-secretkey-generation.html) nelle impostazioni locali per vari motivi:

* se si usa un SCM (per di più condiviso) la secret key può essere visibile al pubblico e quindi portare a problemi di sicurezza (non sono sicuro ma dovrebbe avere a che fare con le autenticazioni), del resto la frase ``# Make this unique, and don't share it with anybody`` presente sopra la sua definizione in ``settings.py`` dovrebbe essere chiara.

* deve essere diversa per ogni installazione, quindi impostata a mano nel ``local_settings.py``.

Rendere ``ROOT_URLCONF`` locale, cioé togliendogli il prefisso con il nome del progetto

```python
 ROOT_URLCONF = 'urls'
```
Indicare la directory dei templates globale 

```python
 TEMPLATE_DIRS = (
     PROJECT_ROOT_PATH + 'templates/'
 )
```
Infine al termine del file inserire questa porzione di codice che legge da un
file locale le impostazioni, in maniera tale da avere per ogni sito la propria
configurazione ottimale 

```python
 # local_settings.py can be used to override environment-specific settings
 # like database and email that differ between development and production.
 try:
     from local_settings import *
 except ImportError:
     print 'Do you have a \'local_settings\'?'
 
 TEMPLATE_DEBUG = DEBUG
 MANAGERS = ADMINS
```
Le ultime due righe permettono di impostare quei valori in base al contenuto di ``local_settings.py``.

## Static Files

Uno dei piccoli problemi che si incontra nel deploy è quello dei file statici
che in un server di produzione non devono essere serviti da django; per la
parte propria di django il seguente pezzo di codice rende i file serviti dal
nostro amato framework sono nel caso in cui si stia eseguendo il debug

```python
 # urls.py
 if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^media/(?P<path>.*)$', 'django.views.static.serve',
			{'document_root': settings.MEDIA_ROOT,
				'show_indexes': True}),
	)
```
Può essere utile anche un file ``.htaccess`` nel caso utilizziate un server Apache con ``mod_rewrite`` abilitato

     RewriteEngine On
     RewriteBase /
     RewriteRule ^(media/.*)$ - [L]
     RewriteRule ^(admin_media/.*)$ - [L]
     RewriteRule ^(dispatch\.fcgi/.*)$ - [L]
     RewriteRule ^(.*)$ dispatch.fcgi/$1 [L]

Per ``admin_media`` è presumibile fare un link simbolico (che si spera il web
server permetta) alla directory ``django/contrib/admin/media/``.

## Mentre si scrive il codice

Personalmente uso un preciso schema per tenere a mente e verificare quali passaggi mancano nel codice

* scrivere un ``FIXME`` o ``TODO`` a seconda dei casi, nelle righe immediatamente vicine a quelle porzioni di codice che necessitano delle migliorie. Per ritrovarle è sufficiente usare il buon veccho ``grep``.

* ricordarsi che se si eseguono dei test che riguardano ``django.contrib.auth`` bisogna includere anche ``django.contrib.admin`` altrimenti vengono a mancare dei templates utili e i tests falliscono.

## Dipendenze

Utilizzando ``pip`` è possibile ottenere un modo automatizzato di
verificare/installare le dovute dipendenze tramite un semplice comando ed in
più ottenere tramite un semplice file di testo l'elenco delle stesse.

Però prima di pensare in un progetto specifico alle dipendenze ritengo più
utile sviluppare le funzionalità di base ottenendo così di non perdere tempo
inutilmente a cambiare di continuo il file delle dipendenze.

Quando ci si ritrova ad un punto “di arrivo” (magari nel deploy su un server
esterno) è possibile usare ``pip`` per ottenere un elenco delle dipendenze che
attualmente sono presenti localmente.

    $ pip freeze

Spesso ci si ritrova a dover lavorare su diversi progetti che devono
condividere la stessa macchina pur non condividendo le stesse librerie (oppure
condividendole ma non le loro versioni utili). Si necessita quindi di avere
degli ambienti puliti e isolati per ogni progetto: a questo serve
``virtualenv``. 

     $ cd path/to/project
     $ virtualenv --no-site-packages env
     New python executable in env/bin/python2.6
     Also creating executable in env/bin/python
     Installing setuptools............done.
     $ source env/bin/activate
     (env) $

Come si può notare il prompt è cambiato e questo indica che si sta usando
esclusivamente il python contenuto dentro la directory env/.

Se si usa debian come distribuzione è possibile che si abbia una versione di
pip un po' obsoleta (tipo 0.3 contro una versione 0.6 disponibile sul sito)
quindi è possibile usare il virtualenv appena impostato e scaricare la nuova
versione 

    (env) $ easy_install pip


e di seguito installare da un file di dipendenze creato precedentemente

    (env) $ pip install -r dependencies.txt # --ignore-installed


**N.B:** attenzione che la variabile ``PYTHONPATH`` non punti da qualche parte esterna al virtualenv in quanto lo scavalcherebbe.

Ancora prima di eseguire un test live tramite l'utilizzo di un browser, nel
caso si stia utilizzando [WSGI/Fcgi](http://www.python.org/dev/peps/pep-0333/)
come interfaccia per eseguire Django sul server potete provare a lanciare da
linea di comando l'eseguibile stesso

    $ PATH_INFO=/path/to/page ./dispatch.fcgi

ed osservare se effettivamente risultano o no errori (``/path/to/page`` è il
percorso della pagina che volete testare il quale, per le specifiche di queste
*gateway interfaces*, deve essere passato attraverso variabili d'ambiente, cioé
``PATH_INFO`` in questo caso).

## Dati iniziali

Una volta caricato il codice sul server è necessario prima di tutto controllare
che il codice funzioni, lanciando gli unit test (perché voi scrivete gli
appositi tests per ogni vostra unità si codice, vero?); in caso contrario
significa che i passaggi effettuati precedentemente sono stati fallaci.

Confermato che il codice funzioni sul vostro server, escludendo problemi di
dipendenze (o al massimo trovandone di nuove :-P) possiamo passare al rendere
operativo il sito; come da manuale, lanciare un syncdb dovrebbe bastare per
risolvere tutti i vostri problemi se avete avuto l'accortezza di inserire
all'interno di una directory ``fixtures`` una fixture appunto, denominata
``initial_data`` relativa a dati fissi del vostro sito (come per esempio delle
flatpages)

    $ python manage.py syncdb

Ma quali sono i dati che in generale sono necessari includere nel progetto?

* Se poi la vostra applicazione/sito fornisce la possibilità di loggarsi, sarà
  d'uopo creare almeno il superuser durante il syncdb; eventualmente si vorrà
creare un utente con permessi limitati (buona pratica di sicurezza, perché voi
ci tenete alla sicurezza, vero?).

```
 $ python manage.py shell
 >>> from django.contrib.auth.models import User
 >>> help(User.objects.create_user)
 Help on method create_user in module django.contrib.auth.models:

 create_user(self, username, email, password=None) method of django.contrib.auth.models.UserManager instance
    Creates and saves a User with the given username, e-mail and password.
 >>> User.objects.create_user('gp', 'gp@no.spam.org', password='password')
```

*  dati relativi alla applicazione ``django.contrib.sites`` che tengano conto dell'effettivo dominio utilizzato dal hosting.

* come detto appena sopra ci possono essere delle pagine che non verranno
  editate frequentemente e magari di carattere generale nel sito le quali
conviene tenere sotto forma di [flatpages](http://docs.djangoproject.com/en/dev/ref/contrib/flatpages/) (basti pensare
alla pagina *about*). Una nota aggiuntiva a questo: il formato migliore per
salvare questo tipo di dato sotto forma di fixture è lo [YAML](http://en.wikipedia.org/wiki/YAML), il quale permette di avere del codice
molto più pulito e [leggibile rispetto all'XML e JSON](http://docs.djangoproject.com/en/dev/howto/initial-data/#providing-initial-data-with-fixtures),
formati standard di solito usati in Django. Questo semplicemente perché
permette di poter preservare newline. Leggibilità prima di tutto.

## Backup

Non vi crederete mica che una volta messo su il sito voi abbiate finito? esiste
il problema dell'eventuale backup che è sempre meglio fare, perché per quanto
siate intelligenti e fortunati l'imprevedibile è sempre in agguato e perdere
magari [anni di lavoro non è mai bello](http://www.codinghorror.com/blog/archives/001315.html). Tralasciamo quale
sia la migliore via per fare un backup, limitandoci a pensare al **come** e non
al **dove** (non che il dove non sia già [impegnativo](http://jwz.livejournal.com/801607.html)); come sempre ci sono due vie

* fare il dump del database nel suo formato proprio (le sfilze di ``CREATE TABLE``, ``INSERT`` per capirci)

* fare il dump attraverso il comando [dumpdata](http://docs.djangoproject.com/en/1.1/ref/django-admin/#dumpdata-appname-appname-appname-model) proprio di Django.

La seconda via è molto più comoda nel caso in cui ci si ritrovi a dover
ricaricare i dati in un progetto simile, tuttavia se non si ha la possibilità
di utilizzare [django-admin](http://docs.djangoproject.com/en/1.1/ref/django-admin/#ref-django-admin) si
ha un cumulo di dati non direttamente importabili. Al contrario è possibile
ricaricare in qualunque caso i dati dumpati con il database nel suo formato
nativo.
