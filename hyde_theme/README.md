This is an *import* of the [hyde theme](http://hyde.getpoole.com/) into the Django template language.

Obviously is not a drop-in import, a lot of work has been done in order
to make it work flawless.

## TODO

 - Create a context processor that inject into the template the ``site`` variable.
 - In order to create a general theming *strategy*, impose ``post`` as variable name
 - setup.py with dependencies (django-pagination)