from django import forms


class ParamForm(forms.Form):
    annee = forms.CharField()
    dimension = forms.CharField()
