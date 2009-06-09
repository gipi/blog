from django.forms import ModelForm, Textarea, CharField
from snippet.models import Entry

class EntryForm(ModelForm):
    content = CharField(widget=Textarea(
	    attrs={'style': 'width:80em;height:40em;'}))

    class Meta:
        model = Entry
