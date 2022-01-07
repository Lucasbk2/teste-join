from django.db import models

# Create your models here.

class Ponto(models.Model):
    nome = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=22, decimal_places=16)
    longitude = models.DecimalField(max_digits=22, decimal_places=16)
    data_expiracao = models.DateField(verbose_name='Data de Expiração')