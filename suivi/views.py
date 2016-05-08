# coding=utf8

from django.shortcuts import render
from importation.models import Parametre, Mesure, DimensionTypeConsommation, DimensionZone
from forms import ParamForm
from datetime import datetime
from django.http import Http404
from operator import itemgetter


def dashboard(request):
    """
    Afficher tableau de bord par defaut
    :param request:
    :return:
    """
    page = "tableaubord"

    # get paramters
    parametres = Parametre.objects.all()
    if parametres:
        parametres = parametres[0]
        an_max = int(parametres.annee_max)
        an_min = int(parametres.annee_min)
        liste_mesure = parametres.liste_mesure

        annees = list()
        for i in range(an_min, an_max + 1):
            annees.append(i)

        # Liste des années
        x_axis = list()
        for annee in range(an_min, (an_max + 1), 1):
            for mois in range(1, 13):
                x_axis.append(datetime(annee, mois, 1))

        mesures = Mesure.objects.all()

        # Pies data
        pies = list()
        for mesure in mesures:
            nom = mesure.nom_mesure
            vente = 0
            for donnee in mesure.donnees:
                vente += donnee.vente
            pie = {"nom": nom, "vente": vente}
            pies.append(pie)

        # Evolution data
        evolution = list()
        for mesure in mesures:
            mesure_data = dict()
            mesure_data['nom_mesure'] = mesure.nom_mesure
            globale = 0
            globale_annee_prec = 0
            # Vente du mois de décembre de l'année précédente
            initial = -1
            for donnee in mesure.donnees:
                if donnee.date == datetime(an_max-1, 12, 1):
                    initial = donnee.vente
                if (donnee.date >= datetime(an_max-1, 1, 1)) and (donnee.date <= datetime(an_max-1, 12, 1)):
                    globale_annee_prec += donnee.vente
            # Ventes et évolutions
            data = list()
            for i in range(1, 13):
                datai = dict()
                ventei = evolutioni = '-'
                for donnee in mesure.donnees:
                    if donnee.date == datetime(an_max, i, 1):
                        ventei = donnee.vente
                        globale += donnee.vente
                        if initial > 0:
                            evolutioni = (float((ventei - initial)) / float(initial)) * 100
                        if initial == 0:
                            evolutioni = 100
                        initial = ventei
                        break
                datai['vente'] = ventei
                datai['evolution'] = evolutioni
                data.append(datai)
            mesure_data['data'] = data
            mesure_data['vente_globale'] = float(globale - globale_annee_prec) / globale_annee_prec * 100
            evolution.append(mesure_data)
    else:
        message = "No data available!"

    return render(request, 'suivi/default_dashbord1.html', locals())


def details(request):
    """
    Afficher les détails de chaque type de consommation.
    :param request:
    :return:
    """
    page = "tableaubord"
    # get paramters
    parametres = Parametre.objects.all()
    if parametres:
        parametres = parametres[0]
        an_max = int(parametres.annee_max)
        an_min = int(parametres.annee_min)

        annees = list()
        for i in range(an_min, an_max + 1):
            annees.append(i)

        selected_year = an_max
        slected_dimesion = 'Types de consommations'

        # Liste des années
        x_axis = list()
        for annee in range(an_min, (an_max + 1), 1):
            for mois in range(1, 13):
                x_axis.append(datetime(annee, mois, 1))

        if request.GET.get('type_vente'):
            type_vente = request.GET['type_vente']
            types_vente_data = Mesure.objects.filter(nom_mesure=type_vente)

            if not types_vente_data:
                raise Http404

            pies = None

            if request.method == "POST":
                form = ParamForm(request.POST)
                if form.is_valid():
                    selected_year = form.cleaned_data["annee"]
                    slected_dimesion = form.cleaned_data["dimension"]

            if slected_dimesion is "Types de consommations":
                data = DimensionTypeConsommation.objects.filter(nom_mesure=type_vente)
                pies = type_conso_pies_data(data, selected_year)

            if slected_dimesion == "Zones":
                date = DimensionZone.objects.filter(nom_mesure=type_vente)

            if slected_dimesion == "Villes":
                pass

        pies = sorted(pies, key=itemgetter('vente'), reverse=True)

        # mesures = Mesure.objects.all()
    else:
        message = "No data available!"

    return render(request, 'suivi/suivi.html', locals())


def type_conso_pies_data(dimensions, annee):
    pies = list()
    for dimension in dimensions:
        nom = dimension.nom_type_consommation
        vente = 0
        for donnee in dimension.donnees:
            if (donnee.date >= datetime(annee, 1, 1)) and (donnee.date <= datetime(annee, 12, 1)):
                vente += donnee.vente
        pie = {"nom": nom, "vente": vente}
        pies.append(pie)

    return pies
