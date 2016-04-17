from django.shortcuts import render
from importation.models import Fichier
from budgetiser.forms import PrevisionForm
from datetime import datetime
import pandas as pd
# from django_pandas.io import read_frame
import pycast as pc


# Effectuer l'analyse descriptive
def analyse_desciptive(request):
    page = "budget"
    # fichiers = Fichier.objects.all()

    return render(request, 'budgetiser/analyse.html', locals())


def prevision(request):
    page = "budget"
    if request.method == "POST":
        form = PrevisionForm(request.POST)
        if form.is_valid():
            annee_prevision = form.cleaned_data["annee_prevision"]
            max_interval = form.cleaned_data["max_interval"]
            min_interval = form.cleaned_data["min_interval"]
            methode = form.cleaned_data["methode"]
            annee_prevision = max_interval + 1
            annees = range(min_interval, max_interval)
            fichiers = Fichier.objects.filter(ventes__date__gte=datetime(min_interval, 1, 1))
            villes = set()
            types_vente = set()
            colones = ["typeVente", "typeConsommation", "zone",  "ville", "date", "vente"]
            lignes = list()
            for fich in fichiers:
                for vente in fich.ventes:
                    villes.add(vente.ville)
                    types_vente.add(vente.typeVente)
                    ligne = [vente.typeVente, vente.typeConsommation, vente.zone, vente.ville, vente.date, vente.vente]
                    lignes.append(ligne)
            dataframe = pd.DataFrame(lignes, columns=colones)
            # valeurs = dataframe.values
            """for type_vente in types_vente:
                for ville in villes:
                    pass"""
            dataf = dataframe[(dataframe.typeVente == "Ventes hors taxes") & (dataframe.ville == "Kolda")]
            serie = pd.Series(dataf["vente"].values, index=dataf["date"].values)
            result = pd.Series()

            if methode == "Winter":
                winter = pc.methods.exponentialsmoothing.HoltWintersMethod(seasonLength=3, valuesToForecast=12)
                result = winter.execute(serie)
            elif methode == "Holt":
                pass
        else:
            message = "Erreur!"
    else:
        fichiers = Fichier.objects.all()
        max_interval = fichiers[0].ventes[0].date.year
        min_interval = fichiers[0].ventes[0].date.year
        for fich in fichiers:
            for vente in fich.ventes:
                if max_interval < vente.date.year:
                    max_interval = vente.date.year
                if min_interval > vente.date.year:
                    min_interval = vente.date.year
        annees = range(min_interval, max_interval)
        annee_prevision = max_interval + 1
    return render(request, 'budgetiser/prevision.html', locals())
