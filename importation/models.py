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
    vente = IntField(required=True)


class Fichier(Document):
    importDate = DateTimeField(auto_now=False)
    editDate = DateTimeField(default=datetime.datetime.now())
    description = StringField(required=False)
    # fichier = FileField(upload_to="files/")
    ventes = ListField(EmbeddedDocumentField(Vente))
