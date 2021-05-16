<!--
.. title: RFC and stuff like that
.. slug: rfc-and-stuff-like-that
.. date: 2012-08-01 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Siccome al lavoro mi sono ritrovato ad imprecare contro il trasporto di dati in una ``POST`` sommarizzo qui le mie scoperte con un tocco di magia ``*NIX``

usando il seguente script ``PHP``

.. code-block:: php

 <?
	if (!empty($_GET["raw"])) {
		print("--SERVER--\n");
		print_r($_SERVER);

		print("--REQUEST--\n");
		print_r($_REQUEST);

		print("--FILES--\n");
		print_r($_FILES);
	}

	if (!empty($_REQUEST["base64"])) {
		print("--BASE64--\n");
		print base64_decode($_REQUEST["base64"]);
	}

	if (!empty($_POST["urlencoded"])) {
		print("Saving urlencoded");
		$handle = fopen("urlencoded", "w");
		if (!$handle) {
			print("Error opening file\n");
			return;
		}
		if (!fwrite($handle, urldecode($_POST["urlencoded"])))
			print("Error writing file");
		else
			print("... Ok\n");
	}

 ?>

si può costruire da linea di comando una ``POST`` in ``HTTP`` usando ``curl(1)``; in questo esempio passo una variabile testuale ed una immagine ``JPEG`` come se fossero generate da una form

.. code-block:: shell

 $ curl http://127.0.0.1:8000/decode.php \
     -H "Content-Type: multipart/form-data; boundary=miao" \
     --data-binary '--miao
 content-disposition: form-data; name="user"

 bau
 --miao
 content-disposition: form-data; name="file"; filename="miao.jpg"
 content-type: image/jpg

 $(convert -size 8x8 xc:white jpg:-)
 --miao--
 '

il responso generato sarà

.. code-block:: text

 Array
 (
     [user] => bau
 )
 Array
 (
     [file] => Array
         (
             [name] => miao.jpg
             [type] => image/jpg
             [tmp_name] => /tmp/phpnkKtlA
             [error] => 0
             [size] => 35
         )
 )


Allora, se si usa il ``Content-Disposition``, seguendo la `RFC2046 <http://www.faqs.org/rfcs/rfc2046.html>`_

  The Content-Type field for multipart entities requires one parameter,
  "boundary". The boundary delimiter line is then defined as a line
  consisting entirely of two hyphen characters ("-", decimal value 45)
  followed by the boundary parameter value from the Content-Type header
  field, optional linear whitespace, and a terminating CRLF.

**URLENCODING**

È possibile utilizzare come encoding il cosiddetto urlencoding (definito nella `RFC1738 <http://www.rfc-editor.org/rfc/rfc1738.txt>`_)
Una cosa da notare con l'urlencoding è che il PHP non gestisce correttamente i NULL byte

  Unsafe:

  Characters can be unsafe for a number of reasons.  The space
  character is unsafe because significant spaces may disappear and
  insignificant spaces may be introduced when URLs are transcribed or
  typeset or subjected to the treatment of word-processing programs.
  The characters "<" and ">" are unsafe because they are used as the
  delimiters around URLs in free text; the quote mark (""") is used to
  delimit URLs in some systems.  The character "#" is unsafe and should
  always be encoded because it is used in World Wide Web and in other
  systems to delimit a URL from a fragment/anchor identifier that might
  follow it.  The character "%" is unsafe because it is used for
  encodings of other characters.  Other characters are unsafe because
  gateways and other transport agents are known to sometimes modify
  such characters. These characters are "{", "}", "|", "\", "^", "~",
  "[", "]", and "`".

  All unsafe characters must always be encoded within a URL. For
  example, the character "#" must be encoded within URLs even in
  systems that do not normally deal with fragment or anchor
  identifiers, so that if the URL is copied into another system that
  does use them, it will not be necessary to change the URL encoding.

**Base64**

Un altra procedura per permettere di trasportare informazioni binarie all'interno di un flusso di testo quale può essere una mail o una pagina web è di usare una codifica che contempli al suo interno solo caratteri ``ASCII``, una di queste è la codifica in base 64. Da come si può intuire dal nome, questa codifica utilizza un alfabeto composto da 64 simboli

.. code-block:: text

 ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/

che come si può notare non interferiscono con il normale funzionamento degli strumenti *plain text*; per farla breve, siccome 64 simboli sono rappresentabili con 6 bits, si prende lo stream di dati che ci interessa, lo si suddivide in blocchi di 3 bytes così da ottenere 4 simboli (:tex:`8 \hbox{bits}\times 3 = 6\hbox{bits}\times 4`). Da notare come lo stream risultante sia di dimensioni maggiori di 1/3 rispetto a quello originale. In caso lo stream non sia composto da un numero di bytes multiplo di 3 si aggiunge un padding di byte nulli e per rendere decodificabile lo stream risultante si aggiunge un padding composto di "=" in uscita.

Se vi interessa una implementazione guardate quella su `wikibooks <http://en.wikibooks.org/wiki/Algorithm_Implementation/Miscellaneous/Base64>`_, se vi interessa sapere meglio come funziona guardate la `RFC2045 <http://www.rfc-editor.org/rfc/rfc2045.txt>`_.