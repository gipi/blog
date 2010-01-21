from django.forms import ModelForm, Textarea, CharField
from snippet.models import Blog

class BlogForm(ModelForm):
    content = CharField(widget=Textarea(
                attrs={'style': 'width:60em;height:20em;'}))

    class Meta:
        model = Blog
        exclude = ['slug', 'user',]
