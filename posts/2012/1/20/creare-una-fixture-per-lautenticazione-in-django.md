<!--
.. title: Creare una fixture per l'autenticazione in Django
.. slug: creare-una-fixture-per-lautenticazione-in-django
.. date: 2012-01-20 00:00:00
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->

Succede spesso durante la creazione dei test per un progetto di aver bisogno di credenziali per un utente fittizio in maniera tale da poter controllare delle view con un utente autenticato

```python

 class CartTest(TestCase):
    fixtures = ['cart.json', 'auth.json']
    def test_add_deal(self):
        client = Client()
        self.assertEqual(client.login(username='pippo', password='pluto'), True)
        # qui altra roba
```

Siccome per avere il json ``auth.json`` bisognerebbe registrarsi effettivamente sulla piattaforma e poi effettuare un bel ``python manage.py dumpdata auth`` e a noi non ci piace, ci leggiamo la documentazione e scopriamo che il formato della password è il seguente



    hashtype$salt$hash

quindi se noi vogliamo la password ``pippo`` con il salt ``7fea6`` hashato con ``sha1`` possiamo utilizzare da linea di comando



    $ echo -n '7fea6''pippo' | sha1sum

A questo punto la seguente fixture può essere scritta

```js

 [
  {
    "model": "auth.user",
    "pk": 1,
    "fields": {
      "username": "pluto",
      "password": "sha1$7fea6$ff1456d2e21736c28046f416c4da647b73520cef"
    }
  }
 ]
```

L'utente ``pippo`` con password ``pluto`` è pronto ad aiutarci nei nostri test.