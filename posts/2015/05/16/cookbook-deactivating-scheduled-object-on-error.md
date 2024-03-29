<!--
.. title: Cookbook: deactivating scheduled object on error
.. slug: cookbook-deactivating-scheduled-object-on-error
.. date: 2015-05-16 00:00:00
.. tags: django,python,unit tests,celery
.. category: 
.. link: 
.. description: 
.. type: text
-->

Suppose we have an object that has a scheduled action on it (do you know celery?)
and suppose that we are far-sighted people and we know that shit happens and we 
want to prevent disaster removing the object from the queue of the scheduler when
an exception is raised.

We are using Django and our object has an attribute ``active`` that indicates
that it is available for scheduling; to manage the exception we add the attribute ``error`` that indicates an error happened on it (probably we could use a ``TextField`` and save also the
exception there but for now is enough); the attribute ``title`` is
here only to have a parameter
to query with the object later, substitute it with the fields that you want, it's
your life.

```python

 class Object(models.Model):
    title  = models.CharField(max_length=100)

    active = models.BooleanField(default=False)
    error  = models.BooleanField(default=False)

    def deactivate(self, error=None):
        if error:
            self.error = True

        self.active = False
        self.save()
```

Suppose the celery task is the following

```python

 @transaction.atomic
 def _manage_obj(pk, *args, **kwargs):
    obj = Object.objects.get(pk=pk)
    do_some_fantastic_action_on_it(obj)
```

the ``transaction.atomic`` decorator make possible to maintain the original state
of the object before the error occurred (also for this reason is necessary to deactivate
it because otherwise the next time the error will happen again 'cause determinism, you know?).

Instead of calling the method below we will use the following code: we call
the original method, wrapping it around a ``try`` and ``except`` block: if an
exception is raised we catch it, we retrieve the object on which the code failed,
we deactivate it indicating that there was an error (probably we should write a decorator here :))

```python
 @app.task
 def manage_object(pk, *args, **kwargs):
    '''
    This method wraps the one managing the object.

    If an exception occurs during the inner method then deactivate
    the object and re-raise the exception so that celery manages it.

    The inner method should be atomic so that the object remains in the
    state it was when the error occurred.
    '''

    try:
        _manage_object(pk, *args, **kwargs)
    except:
        obj = Object.objects.get(pk=pk)
        # get the exception context to reuse later
        exc_info = sys.exc_info()

        obj.deactivate(error=exc_info[0])
        mail_admins('Object deactivate on error', u''''%s' deactivated bc an error occurred.
        ''' % obj.title)

        # reraise exception wo losing traceback
        # http://www.ianbicking.org/blog/2007/09/re-raising-exceptions.html
        raise exc_info[0], exc_info[1], exc_info[2]
```

Since the exception is re-raised, it will be catched by celery that will manage it
in the way is configured for; in order to not lose the original traceback the ``raise``
line has a particular form that you can deduce from the [raise](https://docs.python.org/2.7/reference/simple_stmts.html#raise)
and the [sys.exec_info()](https://docs.python.org/2.7/library/sys.html#sys.exc_info>) references.

## Testing

Obviously the coding is nothin without testing: we need to use the ``mock`` library
to fake an exception and check that the final result is what we expect (you have to
set some django's settings in a particular way to make this works like in the
``override_settings`` just below)

```python
@override_settings(
    CELERY_ALWAYS_EAGER=True,
    CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
    BROKER_BACKEND='memory', # avoid error for missing redis
)
def test_gracefull_failing(self):
    obj = ObjectFactory()
    with mock.patch('my_app.models_tools._manage_object') as mocked_manage_object:
        class KebabException(ValueError):
            pass

        mocked_manage_object.side_effect = KebabException('Kebab is not in the house')

        try:
            manage_object(obj.pk)
        except KebabException as e:
            logger.info('test with ' + str(e))

    # refresh the instance
    obj = Object.objects.get(pk=obj.pk)

    # check something here

```

For now is all, bye.