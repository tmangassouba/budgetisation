# coding=utf8

from django.shortcuts import render
from importation.models import Parametre, Mesure
from datetime import datetime


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

        pies = list()
        for mesure in mesures:
            nom = mesure.nom_mesure
            vente = 0
            for donnee in mesure.donnees:
                vente += donnee.vente
            pie = {"nom": nom, "vente": vente}
            pies.append(pie)
    else:
        message = "No data available!"

    return render(request, 'suivi/default_dashbord1.html', locals())
