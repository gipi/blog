<!--
.. title: passaggio a HTTPS
.. slug: passaggio-a-https
.. date: 2011-07-17 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Da oggi collegandosi al sito è molto probabile che vi si presenterà un avviso da parte del vostro browser indicandovi che il certificato presentato non è trusted; non vi preoccupate, ho solo utilizzato per l'SSL un certificato self-signed (in particolare uno generato per dovecot).

L'unica accortezza è verificare che il fingerprint corrisponda a quello del mio certificato che io posso recuperare utilizzando un magico comando recuperato dalla `FAQ <http://www.madboa.com/geek/openssl/#cert-exam>`_ di openSSL

.. code-block:: text

 # openssl x509 -noout -in /etc/ssl/certs/dovecot.pem -fingerprint
 SHA1 Fingerprint=0B:79:67:F9:E0:A1:DC:7E:11:1C:24:F5:9F:97:76:4F:8B:E1:4D:B6

Se qualcuno che mi legge presenta dei problemi mi avverta (sempre che esista qualcuno che legge quello che scrivo) ;-)