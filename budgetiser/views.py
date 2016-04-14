from django.shortcuts import render
from importation.models import Fichier
import pandas as pd
from django_pandas.io import read_frame


# Effectuer l'analyse descriptive
def analyse_desciptive(request):
    page = "budget"
    # fichiers = Fichier.objects.all()

    return render(request, 'budgetiser/analyse.html', locals())


# Effectuer les prévisions
def prevision(request):
    page = "budget"
    fichiers = Fichier.objects.all()
    dataframe = pd.DataFrame(Fichier.ventes)
    for fich in fichiers:
        data = pd.DataFrame(fich.ventes)
        dataframe.append(data)
    # annee_max = dataframe.loc[:, 'vente'].max
    # annee_min = dataframe[2].min
    return render(request, 'budgetiser/prevision.html', locals())
