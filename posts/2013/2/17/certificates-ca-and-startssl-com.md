<!--
.. title: certificates, CA and startssl.com
.. slug: certificates-ca-and-startssl-com
.. date: 2013-02-17 00:00:00
.. tags: cryptography
.. category: 
.. link: 
.. description: 
.. type: text
-->

Today knowing the technology on which our sites are built is serious business; a
thing that you as informed developer must know is the
[PKI infrastructure](http://en.wikipedia.org/wiki/Public_key_infrastructure>) that is the web of trust used in the modern internet to guarantee security in the communication.

Following Wikipedia, this is the definition:

>A public-key infrastructure (PKI) is a set of hardware, software, people, policies,
>and procedures needed to create, manage, distribute, use, store, and revoke digital certificates.

## Prelude

In order to understand how the PKI works we must do a step back and tell
something about **asymmetric cryptography**: in this scheme you need two keys to
communicate securely contents between parties; if Alice wants to send a message
to Bob she uses his public key, encrypts the message and send to Bob. He using
his private key can decrypt the message and access the original contents. As the
name can make obvious, the public key is **public**, instead the private key
**must remain secret**.

This works using some pretty awesome properties of **prime numbers** and in
general factorization of integer numbers: indeed this scheme is considered
[computational
secure](http://www.cs.princeton.edu/courses/archive/fall07/cos433/lec3.pdf), not
informational secure in the sense that its security is based on a well know hard
problem: factorize numbers. If tomorrow a magician
could factorize instantaneously a 2048 bits numbers then this scheme will be
useless.

The keys are exchangeable in their functionalities: if you use a private key to
encrypt a message, you can use its public key to decrypt, because of this they
are also useful to demonstrate the authenticity of a digital document: if Alice
performs a checksum of her PhD thesis and using her private key encrypts this
value, she can send it to Bob that can at this point use the Alice's public key
to *decrypt* the checksum and compare with the checksum of the document in his
hands. Bob then knows that the document belongs to Alice.
 
 Asymmetric
cryptography therefore can furnish
[authentication](http://en.wikipedia.org/wiki/Authenticity_(disambiguation))
and [confidentiality](http://en.wikipedia.org/wiki/Confidentiality). If
you want to give a try to this kind of cryptography, try
[pgp](http://www.dewinter.com/gnupg_howto/english/GPGMiniHowto.html).

## SSL, TSL and HTTPS

How are used all the crypto stuff in the interwebz? usually they are used by the
**Secure Socket Layer** (also known as **Transport Layer Security**) that
permits to encapsulate an insecure communication channel with a secure one. The
more used protocols have their *secure* version: ``http`` has ``https``,
``imap`` has ``imaps`` etc...

The protocol consists of two distinct phases:

* **Handshake protocol**: authenticate server to client, agree on cryptographic protocols and establish a session key
* **Record protocol**: secure communication using session key

although above we talked about asymmetric encryption, in order to do some crypto
during communication, a simmetric cipher is used since is less expensive from a
computational point of view: the asymmetric crypto is used in the handshake
protocol only to authenticate and to exchange the session key.
 
Indeed is very important that you are sure you are communicating with the right server and not with someone else (since the evil villain would like to intercept the communication *in the middle* of the channel, this kind of attack is called **man in the middle** or ``mitm``); in order to enforce the identity of the endpoint the **PKI** is used.

During the TLS's handshake the server send back to the client a certificate with
some important informations (it's a little bit oversimplificated here)

* signature algorithm
* issuer
* subject
* public key
* signature value

the identity of the server is indicated by the **subject** field (here go things
like domain name and email), the **issuer** field points to the authority that
emitted the certificate and the remaining fields are cryptographic infos. The
most important is the signature value: it's the checksum of the certificate data
(signature excluded) signed with the private key of the issuer; in this way you
are sure that the certification authority has really authorized it.
 
The verification of the identity works as follow: your browser reads the
signature value and using the public key in the issuer's certificate verifies
it, if they match then the browser verifies the issuer's certificate repeating
the process just explained. It's obvious that in theory this process could
continue endlessly but in the reality exists, embedded in your browser
([mozilla](http://www.mozilla.org/projects/security/certs/),
[chromium](http://dev.chromium.org/Home/chromium-security/root-ca-policy)), a
certain
numbers of certificates, called **root certificates**, that are self signed
(i.e. are signed using its own private key verifiable with the public key in the
same certificate). If during the verification process something breaks then the
browser will present you with a message about untrusted transmission.
 

![](https://kb.wisc.edu/images/group1/12473/firefox_connection_untrusted.PNG)

## StartSSL.com

Who emits certificates is called **certification authority** and has its
certificates in the browser as explained just above; they charge people that
wants to have this certificates, but someone gives you certificates for free,
it's [startssl](https://startssl.com). If you don't need high profile
certificates with subdomain and stuffs I advice you to give a try and in this
case to follow the instructions below.

First of all you have to create a pair of public/private keys, in this case we are using ``openssl``

    $ openssl req -new -newkey rsa:2048 -keyout example.com -nodes -out example.com.csr

This generates the two keys (``example.com`` and ``example.com.pub``) and a
**certificate signing request** (``example.com.csr``): roughly speaking it's a
simple certificate without signature that we are going to submit to startssl in
order to have signed with their private key. First of all you have to register,
download the certificate that allows you to authenticate to their services and
then access the web panel and the *certificate wizard* tab as shown in the
following screenshot

![]({{ site.baseurl }}/public/images/certificates/certificates-wizard.png)

After selecting the ``Web Server SSL/TLS Certificate`` from the menu you should
see a page where it asks you to generate a private key.

![]({{ site.baseurl }}/public/images/certificates/generate-keys.png)

Since we have generate our with ``openssl`` we can skip this step and copy the
certificate signing request in the next page.

![]({{ site.baseurl }}/public/images/certificates/submit-certificate-request.png)

If you have already generated your key you can use instead the following command

    $ openssl req -new -key example.com -out example.com.csr

After insert the content of the textarea and submitted you will receive your
signed certificate (I skipped two intermediate pages but are not critical for
the process explained here).

![]({{ site.baseurl }}/public/images/certificates/save-vertificate.png)

The last step is to donwload the root and intermediate certificates and place it
where your server can serve it (for an example of web server configuration with
``nginx`` read the link at the end of the post).

## Application in real life

Keep in mind that all this certificates stuff are used all over, for example
when you develop applications for iPhone you have to sign your code with your
own developer certificate issued from Apple and you have to download their root
certificate and place it in your keychain. In the device should be present a
root certificate that checks the signature on your code if it's authorized from
Apple.
A lot of problems could be avoided just with the right comprehension of the PKI.

## Linkography

Here some links where you can find more informations

* StartSSL [FAQ](https://www.startssl.com/?app=25)
* OpenSSL command line [HowTo](http://www.madboa.com/geek/openssl/)
* setting up https with [nginx](http://www.westphahl.net/blog/2012/01/03/setting-up-https-with-nginx-and-startssl/)
* [CA Certificates tree](http://notary.icsi.berkeley.edu/trust-tree/)