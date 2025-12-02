from django.db import models

class InventarioItem(models.Model):
    nombre = models.CharField(max_length=100)
    cantidad = models.FloatField()
    unidad = models.CharField(max_length=20, default='kg')

    def __str__(self):
        return f"{self.nombre} ({self.cantidad} {self.unidad})"
    
class Racion(models.Model):
    fecha = models.DateField(auto_now_add=True)
    gallinas = models.IntegerField()
    alimento_total = models.FloatField()

    def __str__(self):
        return f"Ración {self.fecha} - {self.gallinas} gallinas"
    
class Produccion(models.Model):
    fecha = models.DateField()
    cantidad = models.IntegerField()

    def __str__(self):
        return f"{self.fecha}: {self.cantidad} huevos"
    

