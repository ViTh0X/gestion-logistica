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


class Proyectos(models.Model):
    id = models.AutoField(primary_key=True)
    nombre_proyecto = models.CharField(max_length=40)
    detalle_proyecto = models.CharField(max_length=120,blank=True,null=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'proyectos'
        
    def __str__(self):
        return self.nombre_proyecto


class Tareas(models.Model):
    id = models.AutoField(primary_key=True)    
    id_proyecto = models.ForeignKey(Proyectos,on_delete=models.CASCADE)
    detalle_tarea = models.CharField(max_length=80)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tareas'
        
    def __str__(self):
        return self.detalle_tarea

class EstadoTareas(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'estado_tareas'
        
    def __str__(self):
        return self.nombre
    

class SubTareas(models.Model):
    id = models.AutoField(primary_key=True)
    id_proyecto = models.ForeignKey(Proyectos,on_delete=models.CASCADE)
    id_tarea = models.ForeignKey(Tareas,on_delete=models.CASCADE)
    detalle_subtarea = models.TextField(max_length=350)
    inicio_actividad = models.DateField()
    fin_actividad = models.DateField()
    responsable_asignado = models.ForeignKey(Responsables, on_delete=models.CASCADE)
    estado_tareas = models.ForeignKey(EstadoTareas,on_delete=models.CASCADE,default=1)  
    fecha_modificacion = models.DateTimeField(auto_now=True)    
      
    class Meta:
        db_table = 'sub_tareas'
    
    def __str__(self):
        return self.detalle_subtarea
    
class GestionSubtareas(models.Model):
    id = models.AutoField(primary_key=True)    
    id_subtarea = models.ForeignKey(SubTareas,on_delete=models.CASCADE)    
    detalle_gestion = models.TextField(max_length=400)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'gestion_subtareas'
        
    def __str__(self):
        return self.id_subtarea.id_tarea.detalle_tarea