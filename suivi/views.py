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
