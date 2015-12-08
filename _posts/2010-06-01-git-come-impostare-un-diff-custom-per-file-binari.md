---
layout: post
title: 'git: come impostare un diff custom per file binari'
comments: true
---
``git`` fondamentalmente è nato per gestire il versioning di codice sorgente
(cioé per farla breve file di testo) quindi qualunque file di tipo diverso, che
lui riconosce come binario, non ha disponibilità di tutte le funzionalità
possibili ed in particolare del diffing. Se per esempio abbiamo sotto
versioning un immagine chiamata ``logo.png``, l'unico messaggio che otteniamo è

```bash
 $ git diff
 diff --git a/logo.png b/logo.png
 index f9e1a4e..2ed156d 100644
 Binary files a/logo.png and b/logo.png differ
```
Nel caso preso ad esempio è possibile customizzare facilmente il diffing impostando il file ``.gitattributes`` segnalando che i file con estensione ``png`` devono essere visualizzati in tal caso usando un comando esterno; poniamo di voler usare ``exiftool``

    *.png diff=exif

possiamo impostare questo programma tramite ``git config``

    $ git config diff.exif.textconv exiftool

Esistono tuttavia dei casi più complicati: per esempio mi sono ritrovato ad
usare [Xmind](http://www.xmind.net/) per gestire l'organizzazione di un
progetto e la cosa fastidiosa era il non sapere esattamente quali parti erano
state modificate fra una sessione di lavoro e l'altra al primo colpo d'occhio;
per ovviare a questo ho dovuto prima capire le caratteristiche del formato in
cui vengono salvati i dati con questo programma: in pratica i file ``.xmind``
sono archivi zip che contengono alcuni files

     $ unzip prova.xmind
     Archive:  prova.xmind
      inflating: meta.xml            
      inflating: content.xml         
      inflating: styles.xml          
      inflating: Thumbnails/thumbnail.jpg  
      inflating: META-INF/manifest.xml

I files sono file ``XML``, purtroppo non indentati, risultando così molto
scomodi da leggere; a questo si può ovviare utilizzando ``xsltproc`` ed un file
``XSLT`` così strutturato

     $ cat indent.xml
     <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
      <xsl:output method="xml" indent="yes"/>
      <xsl:strip-space elements="*"/>
      <xsl:template match="/">
       <xsl:copy-of select="."/>
      </xsl:template>
     </xsl:stylesheet>

nella seguente maniera

    $ xsltproc --novalid indent.xml content.xml

ottenendo in file ``XML`` che è più facile da visualizzare. Unendo questi
piccoli tricks possiamo dare vita al seguente script (chiamiamolo
``dexmind.sh``)

```bash
 #!/bin/bash

 if [ $# -lt 7 ]
 then
	exit 1
 fi

 OLDCWD=$PWD

 TMP=$(mktemp -d)

 cd ${TMP}

 mkdir old
 mkdir new

 OLDFILE="$2"
 NEWFILE="$1"

 unzip "${OLDFILE}" -d old/
 unzip "${OLDCWD}"/"${NEWFILE}" -d new/

 diff -Nur <( xsltproc --novalid indent.xml old/content.xml ) \
         <( xsltproc --novalid indent.xml new/content.xml )

 rm -fr "${TMP}"
```
Quindi se le varie versioni di xmind vengono salvate tramite ``git`` basta impostare nella seguente maniera il repository

     $ cat .gitattributes
     *.xmind diff=xmind
     $ git config diff.xmind.command dexmind.sh

per ottenere una visualizzazione "comoda" utilizzando un semplice ``git diff``.

```diff
--- /dev/fd/63  2010-06-01 12:27:58.002961037 +0200
+++ /dev/fd/62  2010-06-01 12:27:58.002961037 +0200
@@ -275,7 +275,7 @@
                <topic id="3goion232e7fvk0osuq5fbpnj0" timestamp="1274806579104
                  <title>data DDT arrivo</title>
                </topic>
-                <topic id="3364831d74ngrnrcgal21nfsmg" timestamp="1274806583479
+                <topic id="3364831d74ngrnrcgal21nfsmg" style-id="075vnn7k0jvogp
                  <title>giorni giacenza</title>
```
