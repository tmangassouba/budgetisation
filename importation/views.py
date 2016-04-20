# coding=utf8

from django.shortcuts import render, redirect
from django.http import Http404
from importation.forms import FichierForm
from importation.models import Fichier, Vente, Parametre, DimensionTypeConsommation, DimensionZone, Mesure
from xlrd import *
import pandas as pd
import datetime


def accueil(request):
    """
    Page d'accueil, contient le tableau de bord.
    :param request:
    :return: Tableau de bord.
    """
    page = "tableaubord"
    template_name = 'importation/index.html'
    return render(request, 'importation/index.html', locals())


def files_view(request):
    """
    Liste des fichiers importés.
    :param request:
    :return: Page contenant la liste des fichiers importés
    """
    page = "import"
    files_list = Fichier.objects.all()
    return render(request, 'importation/files_list.html', locals())


# Vue pour afficher le contenu d'un ficheir importé
def file_view(request, id_file):
    """
    Le contenu d'un fichier importé.
    :param request:
    :param id_file: identifiant du fichier
    :return:
    """
    page = "import"
    try:
        file_cont = Fichier.objects.get(id=id_file)
    except:
        raise Http404
    return render(request, 'importation/file_cont.html', locals())


def data_view(request):
    """
    Afficher l'esemble des ventes
    :param request:
    :return:
    """
    page = "import"
    data_list = Fichier.objects.all()
    return render(request, 'importation/data_list.html', locals())


# Importer un  fichier
def importer(request):
    """
    Importer un fichier.
    :param request:
    :return:
    """
    page = "import"
    if request.method == "POST":
        form = FichierForm(request.POST, request.FILES)
        if form.is_valid():
            description = form.cleaned_data["description"]
            # cas d'un fichier excel
            if form.cleaned_data["typeFichier"] == "Excel":
                try:
                    excel_file = pd.ExcelFile(form.cleaned_data["fichier"])
                    sheets = excel_file.sheet_names
                    pdf = pd.read_excel(excel_file)
                    message = traitement(pdf, description)
                except XLRDError:
                    message = "Format fichier incorrect"
            # cas d'un fichier CSV
            elif form.cleaned_data["typeFichier"] == "CSV":
                try:
                    excel_file = pd.ExcelFile(form.cleaned_data["fichier"])
                    sheets = excel_file.sheet_names
                    pdf = pd.read_csv(form.cleaned_data["fichier"])
                    message = traitement(pdf, description)
                except XLRDError:
                    message = "Format fichier incorrect"
        else:
            message = "Fields can't be blank !"
    else:
        form = FichierForm()
    return render(request, 'importation/importation.html', locals())


def format_fichier(datatframe):
    """
    Vérifier si le format du fichier import est correcte.
    Le fichier à importer doit avoir les colones suivantes : Années, Type de vente, Type de consommation, Zone
    Stratégique, Ville, janvier, février, mars, avril, mai, juin, juillet, août, septembre, octobre, novembre et
    décembre.
    :param datatframe: Contenu du fichier importé.
    :return: True si le format est correspond, Folse si le format le correspond pas.
    """
    cle = datatframe.columns
    colones_fichier = ["Années",
                       "Type de vente",
                       "Type de consommation",
                       "Zone Stratégique",
                       "Ville",
                       "janvier",
                       "février",
                       "mars",
                       "avril",
                       "mai",
                       "juin",
                       "juillet",
                       "août",
                       "septembre",
                       "octobre",
                       "novembre",
                       "décembre"
                       ]
    return cle == colones_fichier


def traitement(datatframe, description):
    """
    Extrait les données du fichier et les sauvegarde dans labase de données.
    Les données du fichier sont sauvegardées dans la base de données de la façon suivante :
        - typeConsommation
        - zone
        - ville
        - vente
        - date (année, mois)
    :param datatframe: Contenu du fichier (dans un Data Frame).
    :param description: Description du fichier.
    :return message: Notification.
    """
    try:
        # Vérifier si le format du fichier est correct.
        if format_fichier(datatframe) is False:
            raise Exception("Format fichier incorrect!")
        donnees = datatframe.values

        # Récupérer la liste des paramètres (mesures, dimensions, année maximum et année minimum) si ils sont
        # dans labase de données.
        annee_min = None
        annee_max = None
        mesures = set()
        type_consommations = set()
        zones = set()
        villes = set()
        parametre = Parametre.objects.all()
        if parametre:
            annee_min = parametre[0].annee_min
            annee_max = parametre[0].annee_max
            mesures = set(parametre[0].liste_mesure)
            type_consommations = set(parametre[0].liste_type_consommations)
            zones = set(parametre[0].liste_zone)
            villes = set(parametre[0].liste_ville)
            parametre = parametre[0]
            parametre = Parametre.objects.get(id=parametre.id)

        fichier = Fichier()
        fichier.importDate = datetime.datetime.now()
        fichier.editDate = datetime.datetime.now()
        fichier.description = description
        for raw in donnees:
            # Mis à jour année maximum et année minimum
            if (annee_max is None) or (annee_max < raw[0]):
                annee_max = raw[0]
            if (annee_min is None) or (annee_min > raw[0]):
                annee_min = raw[0]

            # Mis à jour des liste des mesures (type de vente), des types de consommation, des zones et des villes.
            mesures.add(raw[1])
            type_consommations.add(raw[2])
            zones.add(raw[3])
            villes.add(raw[4])

            for i in range(5, 17):
                if pd.notnull(raw[i]):
                    vente = Vente()
                    vente.typeVente = raw[1]
                    vente.typeConsommation = raw[2]
                    vente.zone = raw[3]
                    vente.ville = raw[4]
                    vente.date = datetime.datetime(raw[0], i-4, 1)
                    vente.vente = raw[i]
                    fichier.ventes.append(vente)

        # Mis à jour des paramètres.
        if not parametre:
            parametre = Parametre()
        parametre.annee_min = annee_min
        parametre.annee_max = annee_max
        parametre.liste_mesure = list(mesures)
        parametre.liste_type_consommations = list(type_consommations)
        parametre.liste_zone = list(zones)
        parametre.liste_ville = list(villes)
        # parametre.save()

        # Mis à jour des données des mesures, des types de consommation et des zones (Séparer en deux afin de réduire
        # le nombre d'accès à la base de données).
        for mesure in mesures:
            mesure_get = Mesure.objects.get(nom_mesure=mesure)
            for conso in type_consommations:
                type_conso_get = DimensionTypeConsommation.objects.get(nom_mesure=mesure, nom_type_consommation=conso)
                for raw in donnees:
                    pass

        for mesure in mesures:
            mesure_get = Mesure.objects.get(nom_mesure=mesure)
            for zone in zones:
                zone_get = DimensionZone.objects.get(nom_mesure=mesure, nom_type_consommation=conso, nom_zone=zone)
                for raw in donnees:
                    pass

        # Sauvegard du contenu du fichier.
        # fichier.save()
        message = 'Fichier importé avec succès !'
    except UnboundLocalError as e:
        message = e
    except Exception as e:
        message = e

    return message


def delete_file(request, id_file):
    """
    Supprimer un fichier importer.
    :param request:
    :param id_file:bIdentifiant du fichier
    :return:
    """
    page = "import"
    if request.method == "POST":
        try:
            file_cont = Fichier.objects.get(id=id_file)
            file_cont.delete()
            message = "Fichier supprimer avec succès!!"
            return redirect('files_list')
        except:
            raise Http404

    return render(request, 'importation/delete_file.html', locals())


def edit_file(request, id_file):
    """
    Modifier un fichier importé.
    :param request:
    :param id_file:
    :return:
    """
    page = "import"
    try:
        file_cont = Fichier.objects.get(id=id_file)
        ventes = pd.DataFrame(file_cont.ventes)
    except:
        raise Http404
    return render(request, 'importation/edit.html', locals())
