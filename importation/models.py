from mongoengine import *
import datetime


class Utilisateur(Document):
    pseudo = StringField(max_length=20, required=True)
    password = StringField(required=True)
    nom = StringField(max_length=20, required=True)
    prenom = StringField(max_length=20, required=True)
    typeUtilisateur = StringField(max_length=20, required=True)


class Vente(EmbeddedDocument):
    typeVente = StringField(required=True)
    typeConsommation = StringField(required=True)
    zone = StringField(required=True)
    ville = StringField(required=True)
    date = DateTimeField(required=True)
    vente = LongField(required=True)


class Fichier(Document):
    importDate = DateTimeField(auto_now=False)
    editDate = DateTimeField(default=datetime.datetime.now())
    description = StringField(required=True)
    # fichier = FileField(upload_to="files/")
    ventes = ListField(EmbeddedDocumentField(Vente))


class VenteData(Document):
    vente = LongField()
    date = DateTimeField()


class Mesure(Document):
    nom = StringField()
    donnees = ListField(EmbeddedDocumentField(VenteData))


class DimensionTypeConsommation(Document):
    mesure = StringField()
    nom = StringField()
    donnees = ListField(EmbeddedDocumentField(VenteData))


class DimensionZone(Document):
    mesure = StringField()
    type_consommation = StringField()
    nom = StringField()
    donnees = ListField(EmbeddedDocumentField(VenteData))


class Parametre(Document):
    annee_max = IntField()
    annee_min = IntField()
    liste_mesure = ListField()
    liste_dimension = ListField()
    liste_zone = ListField()
    liste_ville = ListField()
