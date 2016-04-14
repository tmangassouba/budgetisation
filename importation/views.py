# coding=utf8

from django.shortcuts import render, redirect
from django.http import Http404
from importation.forms import FichierForm
from importation.models import Fichier, Vente
from xlrd import *
import pandas as pd
import datetime


# accueil
def accueil(request):
    page = "tableaubord"
    template_name = 'importation/index.html'
    return render(request, 'importation/index.html', locals())


# Vue pour afficher l'ensemble des fichier importés
def files_view(request):
    page = "import"
    files_list = Fichier.objects.all()
    return render(request, 'importation/files_list.html', locals())


# Vue pour afficher le contenu d'un ficheir importé
def file_view(request, id_file):
    page = "import"
    try:
        file_cont = Fichier.objects.get(id=id_file)
    except:
        raise Http404
    return render(request, 'importation/file_cont.html', locals())


# Vue pour afficher toutes les ventes
def data_view(request):
    page = "import"
    data_list = Fichier.objects.all()
    return render(request, 'importation/data_list.html', locals())


# Importer un  fichier
def importer(request):
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


# Traitements pour importer les fichiers
def traitement(datatframe, description):
    try:
        donnees = datatframe.values
        cle = list(datatframe.columns)
        # Les noms de colones
        format_fichier = ["Années",
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
        if cle != format_fichier:
            raise Exception('Format fichier incorrect !')
        fichier = Fichier()
        fichier.importDate = datetime.datetime.now()
        fichier.editDate = datetime.datetime.now()
        fichier.description = description
        for raw in donnees:
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
        fichier.save()
        message = 'Fichier importé avec succès !'
    except UnboundLocalError as e:
        message = e
    except Exception as e:
        message = e

    return message


# Supprimer un fichier
def delete_file(request, id_file):
    page = "import"
    if request.method == "POST":
        try:
            file_cont = Fichier.objects.get(id=id_file)
            file_cont.delete()
            return redirect('files_list')
        except:
            raise Http404

    return render(request, 'importation/delete_file.html', locals())


# Modifier un fichier
def edit_file(request, id_file):
    page = "import"
    try:
        file_cont = Fichier.objects.get(id=id_file)
        ventes = pd.DataFrame(file_cont.ventes)
    except:
        raise Http404
    return render(request, 'importation/edit.html', locals())
