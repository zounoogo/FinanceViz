# visualization/models.py

from django.db import models

class Categorie(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom

class Rapport(models.Model):
    titre = models.CharField(max_length=255)
    date_debut = models.DateField()
    date_fin = models.DateField()
    total_ventes = models.DecimalField(max_digits=12, decimal_places=2)
    total_depenses = models.DecimalField(max_digits=12, decimal_places=2)
    total_revenus = models.DecimalField(max_digits=12, decimal_places=2)
    fichier_pdf = models.FileField(upload_to='rapports/pdf/', blank=True, null=True)
    fichier_image = models.FileField(upload_to='rapports/images/', blank=True, null=True)

    def __str__(self):
        return self.titre
