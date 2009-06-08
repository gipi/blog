from django.forms import ModelForm, Textarea, CharField
from snippet.models import Entry

class EntryForm(ModelForm):
    content = CharField(widget=Textarea())

    class Meta:
        model = Entry
