from django.forms import ModelForm, Form, Textarea, CharField, FileField
from yadb.models import Blog


class BlogForm(ModelForm):
    content = CharField(widget=Textarea(
                attrs={'style': 'width:60em;height:20em;'}))

    class Meta:
        model = Blog
        exclude = ['slug', 'user',]

class UploadFileForm(Form):
    file = FileField()
