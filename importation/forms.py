from django import forms
# from importation.models import Fichier


class FichierForm(forms.Form):
    typeFichier = forms.CharField()
    fichier = forms.FileField()
    description = forms.CharField(required=False)
