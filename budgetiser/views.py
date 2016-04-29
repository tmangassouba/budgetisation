# coding=utf8
from django.shortcuts import render
from django.http import Http404
from importation.models import Fichier, Mesure, Parametre, DimensionTypeConsommation, DimensionZone
from budgetiser.forms import PrevisionForm
from datetime import datetime
import pandas as pd
# import numpy as np
import pycast as pc


def analyse_desciptive(request):
    """
    Effectuer analyse descriptive.
    :param request:
    :return:
    """
    page = "budget"

    # get paramters
    parametres = Parametre.objects.all()
    if parametres:
        parametres = parametres[0]
        an_max = int(parametres.annee_max)
        an_min = int(parametres.annee_min)
        if (parametres.annee_min - 5) > an_min:
            an_min = parametres.annee_min - 5
        annees = list()
        for i in range(an_min, an_max + 1):
            annees.append(i)

        # Liste des années
        x_axis = list()
        for annee in range(an_min, (an_max + 1), 1):
            for mois in range(1, 13):
                x_axis.append(datetime(annee, mois, 1))

        if request.GET.get('type_vente'):
            type_vente = request.GET['type_vente']
            types_conso_data = DimensionTypeConsommation.objects.filter(nom_mesure=type_vente)
            # zone_data = DimensionZone.objects.filter(nom_mesure=type_vente)
            zones_data = DimensionZone.objects.filter(nom_mesure=type_vente)
            if not types_conso_data or not zones_data:
                raise Http404
            type_conso_data = consommation_data_to_graph_data(types_conso_data, x_axis)
            zone_data = zone_data_to_graph_data(zones_data, x_axis)

            return render(request, 'budgetiser/analyse_type_vente.html', locals())

        mesures = Mesure.objects.all()
    else:
        message = "No data available!"

    return render(request, 'budgetiser/analyse.html', locals())


def consommation_data_to_graph_data(cosommations_data, x_axis):
    """
    Pour chaque date de l'axe des abscisse mettre 'null' si elle n'a de vente.
    :param cosommations_data: ventes par type de consommation.
    :param x_axis: Dates de l'axe des abscisse
    :return: Ventes par type de consommation avec 'null' pour les mois qui n'ont pas de ventes
    """
    cosommation_data = list()
    for zone in cosommations_data:
        list_d_z = dict()
        list_d_z['nom_type_consommation'] = zone.nom_type_consommation
        d_z_s = list()
        dates_zone = list()
        for date in zone.donnees:
            dates_zone.append(date.date)
        for xx in x_axis:
            d_z = dict()
            d_z['date'] = xx
            if xx in dates_zone:
                for donnee in zone.donnees:
                    if xx == donnee.date:
                        d_z['vente'] = donnee.vente
                        break
            else:
                d_z['vente'] = 'null'
            d_z_s.append(d_z)
        list_d_z['donnees'] = d_z_s
        cosommation_data.append(list_d_z)

    return cosommation_data


def zone_data_to_graph_data(zones_data, x_axis):
    """
    Pour chaque date de l'axe des abscisse mettre 'null' si elle n'a de vente.
    :param zones_data: Ventes par zone.
    :param x_axis: Dates de l'axe des abscisse.
    :return: Ventes par zone avec 'null' pour les mois qui n'ont pas de ventes
    """
    zone_data = list()
    for zone in zones_data:
        list_d_z = dict()
        list_d_z['nom_zone'] = zone.nom_zone
        d_z_s = list()
        dates_zone = list()
        for date in zone.donnees:
            dates_zone.append(date.date)
        for xx in x_axis:
            d_z = dict()
            d_z['date'] = xx
            if xx in dates_zone:
                for donnee in zone.donnees:
                    if xx == donnee.date:
                        d_z['vente'] = donnee.vente
                        break
            else:
                d_z['vente'] = 'null'
            d_z_s.append(d_z)
        list_d_z['donnees'] = d_z_s
        zone_data.append(list_d_z)

    return zone_data


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
            serie = pc.common.timeseries.TimeSeries()
            for data in dataf.values:
                # temps = (data[4] - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
                temps = pc.common.timeseries.TimeSeries.convert_timestamp_to_epoch(data[4].strftime('%Y-%m-%d'), '%Y-%m-%d')
                serie.add_entry(temps, data[5])

            result = pd.Series()

            if methode == "Winter":
                wint = pc.methods.exponentialsmoothing.HoltMethod(valuesToForecast=12)
                result = wint.execute(serie)
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
