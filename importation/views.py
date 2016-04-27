# coding=utf8

from django.shortcuts import render
from django.http import Http404
from importation.forms import FichierForm
from importation.models import Fichier, Vente, Parametre, DimensionTypeConsommation, DimensionZone, Mesure, VenteData
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
    {
     A ajouter :
     - vérifier si la date entrée pour une ville est déjà dans la base de données (isin : pandas).
     - pd.isnull(df1) # Teste si les lignes contiennent ou non NaN
    }
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

        # Data frame contenant les ventes
        ventes_dataframe = pd.DataFrame(list(),
                                        columns=("typeVente", "typeConsommation", "zone", "ville", "date", "vente"))
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
                    # Mettre les ventes dans un Data Frame.
                    ventes_dataframe.loc[len(ventes_dataframe)] = [raw[1], raw[2], raw[3], raw[4], vente.date, raw[i]]
            if ventes_dataframe.empty:
                raise Exception("Data frame dat error !")

        # Mis à jour des paramètres.
        if not parametre:
            parametre = Parametre()
        parametre.annee_min = annee_min
        parametre.annee_max = annee_max
        parametre.liste_mesure = list(mesures)
        parametre.liste_type_consommations = list(type_consommations)
        parametre.liste_zone = list(zones)
        parametre.liste_ville = list(villes)

        # Mis à jour des données des mesures et des types de consommation et des zones
        for mesure in mesures:
            # Mise à jour zone
            for zone in zones:
                zone_get = DimensionZone.objects.filter(nom_mesure=mesure, nom_zone=zone)
                if zone_get:
                    zone_get = DimensionZone.objects.get(id=zone_get[0].id)
                else:
                    zone_get = DimensionZone()
                    zone_get.nom_mesure = mesure
                    zone_get.nom_zone = zone
                    zone_get.donnees = list()
                ventes_zone = ventes_dataframe[(ventes_dataframe.typeVente == mesure) &
                                               (ventes_dataframe.zone == zone)].groupby('date').sum()
                if not ventes_zone.empty:
                    for i in range(0, len(ventes_zone.values)):
                        vent = VenteData()
                        vent.vente = ventes_zone.values[i]
                        vent.date = ventes_zone.index[i]
                        zone_get.donnees.append(vent)
                    zone_get.save()
            # fin mise à jour zone

            # Mise à jour dimension (type de consommation)
            for conso in type_consommations:
                type_conso_get = DimensionTypeConsommation.objects.filter(nom_mesure=mesure,
                                                                          nom_type_consommation=conso)
                if type_conso_get:
                    type_conso_get = DimensionTypeConsommation.objects.get(id=type_conso_get[0].id)
                else:
                    type_conso_get = DimensionTypeConsommation()
                    type_conso_get.nom_mesure = mesure
                    type_conso_get.nom_type_consommation = conso
                    type_conso_get.donnees = list()

                ventes_dim = ventes_dataframe[(ventes_dataframe.typeVente == mesure) &
                                              (ventes_dataframe.typeConsommation == conso)].groupby('date').sum()
                if not ventes_dim.empty:
                    for i in range(0, len(ventes_dim.values)):
                        vent = VenteData()
                        vent.vente = ventes_dim.values[i]
                        vent.date = ventes_dim.index[i]
                        type_conso_get.donnees.append(vent)
                    type_conso_get.save()
            # fin mise à jour dimension(type de consommation)

            # Mise à jour Mesure (Type de vente)
            mesure_get = Mesure.objects.filter(nom_mesure=mesure)
            if mesure_get:
                mesure_get = Mesure.objects.get(id=mesure_get[0].id)
            else:
                mesure_get = Mesure()
                mesure_get.nom_mesure = mesure
                mesure_get.donnees = list()
            ventes_mes = ventes_dataframe[ventes_dataframe.typeVente == mesure].groupby('date').sum()
            if not ventes_mes.empty:
                for i in range(0, len(ventes_mes.values)):
                    vent = VenteData()
                    vent.vente = ventes_mes.values[i]
                    vent.date = ventes_mes.index[i]
                    mesure_get.donnees.append(vent)
                mesure_get.save()
            # fin mise à jour mesure

        # Sauvegard du contenu du fichier et des paramétres
        parametre.save()
        fichier.save()
        message = 'Fichier importé avec succès !'
    except UnboundLocalError as e:
        message = e
    except Exception as e:
        message = e

    return message


def delete_file(request, id_file):
    """
    Supprimer un fichier importer et mis à jour des mesures et dimentions
    :param request:
    :param id_file: Identifiant du fichier
    :return:
    """
    page = "import"
    try:
        file_cont = Fichier.objects.get(id=id_file)
    except Fichier.DoesNotExist:
        raise Http404
    except Exception:
        raise Http404

    if request.method == "POST":
        try:
            # Récupérer les données dans un Data Frame
            ventes = pd.DataFrame(list(), columns=("typeVente", "typeConsommation", "zone", "ville", "date", "vente"))
            for vente in file_cont.ventes:
                ligne_vente = [vente.typeVente, vente.typeConsommation, vente.zone, vente.ville, vente.date, vente.vente]
                ventes.loc[len(ventes)] = ligne_vente

            # Get parameters
            parametre = Parametre.objects[:1]
            if not parametre:
                raise Exception("Delete_error_no_panameter")
            annee_min = parametre.annee_min
            annee_max = parametre.annee_max
            mesures = set(parametre.liste_mesure)
            type_consommations = set(parametre.liste_type_consommations)
            zones = set(parametre.liste_zone)
            villes = set(parametre.liste_ville)

            # Mise à jour des données des mesures et des dimensions
            """for mesure in mesures:
                for conso in type_consommations:
                    for zone in zones:
                        ventes_zone = ventes[(ventes.typeVente == mesure) &
                                             (ventes.typeConsommation == conso) &
                                             (ventes.zone == zone)
                                             ].groupby('date').sum()
                        if not ventes_zone.empty:
                            for vz in ventes_zone:
                                lzone = DimensionZone.objects(nom_mesure=mesure,
                                                              nom_type_consommation=conso,
                                                              nom_zone=zone,
                                                              donnees__date=vz.date
                                                              )[:1]
                                lzone.donnees.vente = lzone.donnees.vente - vz.vente
                                if lzone.donnees.vente == 0:
                                    lzone.donnees.remove()
                                lzone.save()"""

            # file_cont.delete()
            message = "Fichier supprimé avec succès !"
            # return redirect('files_list', locals())
        except Exception as e:
            message = e

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
