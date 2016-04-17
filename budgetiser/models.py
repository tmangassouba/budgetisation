from __future__ import unicode_literals
from mongoengine import *
from django.db import models
from importation.models import Vente


class Prevision(models.Model):
    date = DateTimeField()
    annee_prevision = IntField()
    max_interval = IntField()
    min_interval = IntField()
    methode = StringField()
    ventes_prevus = ListField(EmbeddedDocumentField(Vente))
