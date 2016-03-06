---
layout: post
title: 'Creating a linked instance in an add page'
comments: true
tags: [django, python]
---
Suppose we have a model named ``Provider`` having a foreign key to an instance of
``User`` needed in order to allow a human to login and do stuff in the backoffice.

```python

 class Provider(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
```

(``settings.AUTH_USER_MODEL`` should be used to avoid rewriting a lot of code if you are using
a custom user model).

Suppose the backoffice has different access capabilities represented by different ``Group`` instances and the ``GROUP_ADMIN_NAME`` allow the user belonging to it to add instances
of``Provider``and the instances of ``Provider`` need to have ``GROUP_PROVIDER_NAME`` attached to them.

Obviously attaching an user in the add form for the ``Provider`` is not a problem, Django
creates an UI to do that, but also without thinking about the problem involved allowing to
someone to create an user, attaching the correct group to the just created user can be
error prone and it's a good rule of thumb avoid human skills in order to make the system work.

## Solution

The idea is to modify the add form in order to show two more fields, ``username`` and ``password``
that will be used to create the given user after saving the initial model instance; 

The implementation shown below simply create a custom form with that two fields and is
used only when the object is created but not changed. The correct configuration of
the user is done in the ``save_model()`` method of the ``ProviderAdmin`` class 
(checking that the instance is added and not changed).


```python

 class ProviderAdminFormAdd(forms.ModelForm):
    class Meta:
        exclude = [
            'user',
        ]

    username = forms.CharField()
    password = forms.CharField(widget=forms.widgets.PasswordInput)

 class ProviderAdmin(admin.ModelAdmin):
    readonly_fields = (
        'user', # this override the form's exclude attribute
    )
    def get_form(self, request, obj=None, **kwargs):
        if not obj:
            kwargs['form'] = ProviderAdminFormAdd
        return super(ProviderAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        '''Link a just created user with the instance.'''
        if not change:
            user = settings.AUTH_USER_MODEL.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )

            user.groups.add(Group.objects.get(name=GROUPS_PROVIDER_NAME))
            user.save()

            obj.user = user

        super(ProviderAdmin, self).save_model(request, obj, form, change)
```

In order to complete the implementation we need some testing (I like [testing]({% post_url 2012-12-19-the-amazing-world-of-python-testing %})):
in the code just below we have two tests, in the first we are checking that
the page doesn't give an error when accessed (i.e. by a simple ``GET``
request with a logged user) and the needed fields ``username`` and ``password``
are present.

When a ``POST`` is done with the correct data then a new ``Provider`` instance
is created with an attached ``User`` to it.

The second test checks that the change interface doesn't have the added fields.


```python

    def test_provider_add_with_user(self):
        n_users_start = User.objects.all().count()
        n_providers_start = Provider.objects.count()

        url = reverse('admin:deal_provider_add')
        self.assertEqual(True, self.client.login(username=self.amministratore.username, password='password'))

        # check accessing the page is ok
        response = self.client.get(url)
        n_providers_end = Provider.objects.all().count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(n_providers_end, n_providers_start)

        # it's not possible to retrieve the original class
        form = response.context['adminform']
        # so we check for fields
        self.assertTrue('username' in form.form.fields)
        self.assertTrue('password' in form.form.fields)

        # check empty form
        response = self.client.post(url)
        n_providers_end = Provider.objects.all().count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(n_providers_end, n_providers_start)

        form =  response.context['adminform']

        data = {
            'username':    'user-name',
            'password':    'password',
            '_save':       '',
        }
        response = self.client.post(url, data=data)
        n_users_end = User.objects.all().count()
        n_providers_end = Provider.objects.all().count()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(n_providers_end, n_providers_start + 1)
        self.assertEqual(n_users_end, n_users_start + 1)

        # FIXME: check Group and login maybe and stuff

    def test_provider_change_is_normal(self):
        '''We don't want customization for the change form'''
        n_users_start = User.objects.all().count()
        n_providers_start = Provider.objects.count()

        url = reverse('admin:deal_provider_change', args=[1,])
        self.assertEqual(True, self.client.login(username=self.amministratore.username, password='password'))

        # check accessing the page is ok
        response = self.client.get(url)
        n_providers_end = Provider.objects.all().count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(n_providers_end, n_providers_start)

        # it's not possible to retrieve the original class
        form = response.context['adminform']
        # so we check for fields
        self.assertTrue('username' not in form.form.fields)
        self.assertTrue('password' not in form.form.fields)
```

## Extra

Just for reference I add the flow of the [internal implementation](https://github.com/django/django/blob/1.7.8/django/contrib/admin/options.py#L515)
of Django

```

 self.add_view()
 '-> self.changeform_view(obj=None)
   '-> self.get_form()
   '-> self.save_form(form)
     '-> form.save(commit=False)
     '-> self.save_model()
     '-> self.save_related()
     '-> self.response_add()
```
