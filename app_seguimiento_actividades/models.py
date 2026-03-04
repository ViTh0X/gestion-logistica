from django.db import models

# Create your models here.

class Responsables(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=60)
    empresa = models.CharField(max_length=80)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'responsables'
        
    def __str__(self):
        return self.nombre

class Actividades(models.Model):
    id = models.AutoField(primary_key=True)
    nombre_actividad = models.CharField(max_length=40)
    detalle_actividad = models.CharField(max_length=120)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'actividades'
        
    def __str__(self):
        return self.nombre_actividad
    
class DetalleActividades(models.Model):
    id = models.AutoField(primary_key=True)
    detalle_actividad = models.TextField(max_length=600)
    inicio_actividad = models.DateTimeField()
    fin_actividad = models.DateTimeField()
    responsable_asignado = models.ForeignKey(Responsables, on_delete=models.CASCADE)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'detalle_actividades'
    
    def __str__(self):
        return self.detalle_actividad