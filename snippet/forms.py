from django.forms import ModelForm, Form, Textarea, CharField, FileField
from snippet.models import Entry, Blog

class EntryForm(ModelForm):
    content = CharField(widget=Textarea(
                attrs={'style': 'width:60em;height:10em;'}))

    class Meta:
        model = Entry
        exclude = ['user',]

class BlogForm(ModelForm):
    content = CharField(widget=Textarea(
                attrs={'style': 'width:60em;height:20em;'}))

    class Meta:
        model = Blog
        exclude = ['slug', 'user',]

class UploadFileForm(Form):
    file = FileField()
