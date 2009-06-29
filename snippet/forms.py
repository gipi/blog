from django.forms import ModelForm, Textarea, CharField
from snippet.models import Entry

class EntryForm(ModelForm):
    content = CharField(widget=Textarea(
	    attrs={'style': 'width:60em;height:10em;'}))

    class Meta:
        model = Entry
