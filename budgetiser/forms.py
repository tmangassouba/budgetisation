from django import forms


class PrevisionForm(forms.Form):
    annee_prevision = forms.IntegerField()
    max_interval = forms.IntegerField()
    min_interval = forms.IntegerField()
    methode = forms.CharField()
