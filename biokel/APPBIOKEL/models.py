from django.db import models

class InventarioItem(models.Model):
    nombre = models.CharField(max_length=100)
    cantidad = models.FloatField()
    unidad = models.CharField(max_length=20, default='kg')

    def __str__(self):
        return f"{self.nombre} ({self.cantidad} {self.unidad})"