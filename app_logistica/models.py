from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator
import hashlib
import os



# Create your models here.
class Colaboradores(models.Model):
    codigo_colaborador = models.AutoField(primary_key=True)
    nombre_colaborador = models.CharField(max_length=150)
    usuario_sistema = models.CharField(max_length=25)
    correo = models.CharField(max_length=50)
    usuario_sentinel = models.CharField(max_length=15)
    usuario_sbs = models.CharField(max_length=15)
    usuario_windows = models.CharField(max_length=15)
    usuario_reloj_control = models.CharField(max_length=15)
    codigo_impresion_colaborador = models.CharField(max_length=20)
    cargo_colaborador = models.ForeignKey('CargoColaboradores', models.DO_NOTHING)
    fecha_modificacion = models.DateTimeField()
    estado_colaboradores = models.ForeignKey('EstadoColaboradores', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'colaboradores'            
        
    def __str__(self):
        return self.nombre_colaborador

class CargoColaboradores(models.Model):
    codigo_cargo = models.AutoField(primary_key=True)
    nombre_cargo = models.CharField(max_length=60)

    class Meta:
        managed = False
        db_table = 'cargo_colaboradores'


class EstadoColaboradores(models.Model):
    codigo_estado = models.AutoField(primary_key=True)
    nombre_estado = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'estado_colaboradores'      
        
        
class AreasEmpresa(models.Model):
    id_area = models.AutoField(primary_key=True)
    nombre_area = models.CharField(max_length=40)
    descripcion_area = models.CharField(max_length=150)
    fecha_modificacion = models.DateTimeField(auto_now=True)
        
    class Meta:
        db_table = 'areas_empresa'
        
    def __str__(self):
        return self.nombre_area
    
    
class Almacenes(models.Model):
    id_almacen = models.AutoField(primary_key=True)
    nombre_almacen = models.CharField(max_length=60)
    descripcion_almacen = models.CharField(max_length=150)
    direccion_almacen = models.CharField(max_length=120)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'almacences'
    
    def __str__(self):
        return self.nombre_almacen
    

class TipoEstadoItems(models.Model):
    id_estado = models.AutoField(primary_key=True)
    nombre_estado = models.CharField(max_length=60)
    descripcion_estado = models.CharField(max_length=150)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tipo_estado_items'
        
    def __str__(self):
        return self.nombre_estado
    
class TipoItems(models.Model):
    id_tipo = models.AutoField(primary_key=True)
    nombre_tipo = models.CharField(max_length=60)
    decripcion_tipo = models.CharField(max_length=150)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tipo_items'
    
    def __str__(self):
        return self.nombre_tipo

class Proveedores(models.Model):
    id_proveedor = models.AutoField(primary_key=True)
    documento = models.CharField(max_length=12,unique=True)
    nombre = models.CharField(max_length=120)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'proveedores'
        
    def __str__(self):
        return self.nombre
    
class TipoMoneda(models.Model):
    ip_tipo_moneda = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=10)
    logo = models.CharField(max_length=1)
    fecha_modificacion =  models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tipo_moneda'
        
    def __str__(self):
        return self.nombre
    
    
class Items(models.Model):
    id_item = models.AutoField(primary_key=True)
    comprobante_contable = models.CharField(max_length=20,blank=True,null=True)
    fecha_contable = models.DateField(blank=True,null=True)
    factura_boleta = models.CharField(max_length=20,blank=True,null=True)
    tipo_item = models.ForeignKey(TipoItems,on_delete=models.CASCADE)#desarrollo
    #tipo_item = models.ForeignKey(TipoItems,on_delete=models.CASCADE)#,null=True,blank=True)produccion
    nombre_item = models.CharField(max_length=100)
    marca_item = models.CharField(max_length=20, blank=True, null=True)    
    modelo_item = models.CharField(max_length=20, blank=True, null=True)
    serie_item = models.CharField(max_length=20, blank=True,null=True)
    imagen_qr = models.ImageField(upload_to='imagenes_qr/',blank=True,null=True)    
    cantidad_items = models.IntegerField(default=0)
    tipo_moneda = models.ForeignKey(TipoMoneda,on_delete=models.CASCADE,default=1)    
    precio_unitario = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal('0.00'),validators=[MinValueValidator(Decimal('0.00'))])
    proveedor = models.ForeignKey(Proveedores,on_delete=models.CASCADE,null=True,blank=True)
    id_area = models.ForeignKey(AreasEmpresa,on_delete=models.CASCADE,null=True,blank=True)
    id_estado = models.ForeignKey(TipoEstadoItems,on_delete=models.CASCADE,null=True,blank=True)
    id_almacen = models.ForeignKey(Almacenes,on_delete=models.CASCADE,null=True,blank=True)
    id_usuario = models.ForeignKey(Colaboradores,on_delete=models.CASCADE,null=True,blank=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'items'
    
    def __str__(self):
        return self.nombre_item
    
    
class HistorialInventarios(models.Model):
    id_historial = models.AutoField(primary_key=True)
    id_item = models.ForeignKey(Items,on_delete=models.CASCADE)
    nombre_area = models.CharField(max_length=40)
    nombre_almacen = models.CharField(max_length=60)
    nombre_usuario = models.CharField(max_length=150)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'historial_inventarios'
        
    def __str__(self):
        return self.id_historial
    
    
class TiposMovimiento(models.Model):
    id_tipo = models.AutoField(primary_key=True)
    nombre_movimiento = models.CharField(max_length=60)
    decripcion_tipo = models.CharField(max_length=150)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tipos_movimiento'
        
    def __str__(self):
        return self.nombre_movimiento
    
        
class ItemMovimientosCabecera(models.Model):
    id_cabecera = models.AutoField(primary_key=True)
    colaborador_confirma = models.ForeignKey(Colaboradores,on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now=True)
    firma_base64 = models.TextField()
    hash_seguridad = models.CharField(max_length=64, editable=False)
    pdf_archivo = models.FileField(upload_to='pdfs_movimientos/', null=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.hash_seguridad:
            # Sello de seguridad
            cadena = f"{self.colaborador_confirma}{self.fecha}{self.firma_base64}{settings.SECRET_KEY}"
            self.hash_seguridad = hashlib.sha256(cadena.encode()).hexdigest()
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'items_movimientos_cabezera'
    
    def __str__(self):
        return f"Cabezera {self.id_cabezera} - {self.colaborador_confirma}"
    
class ItemsMovimientos(models.Model):
    id_movimiento = models.AutoField(primary_key=True)
    id_movimiento_cabezera = models.ForeignKey(ItemMovimientosCabecera,on_delete=models.CASCADE)
    id_item = models.ForeignKey(Items,on_delete=models.CASCADE)
    voucher = models.CharField(max_length=15,blank=True,null=True)
    referencia = models.CharField(max_length=15,blank=True,null=True)
    fecha_contable = models.DateField(blank=True,null=True)
    factura = models.CharField(max_length=15,blank=True,null=True)
    proveedor = models.ForeignKey(Proveedores,on_delete=models.CASCADE,blank=True,null=True)
    #tipo_movimiento = models.ForeignKey(TiposMovimiento,on_delete=models.CASCADE)#,null=True,blank=True)#produccion    
    tipo_movimiento = models.ForeignKey(TiposMovimiento,on_delete=models.CASCADE)#desarrollo    
    nombre_origen = models.CharField(max_length=150,blank=True,null=True)
    nombre_destino = models.CharField(max_length=150)
    cantidad_movimiento = models.IntegerField(default=1)
    id_movimiento_referencia = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True)
    observaciones = models.CharField(max_length=200,default="Sin Observaciones")
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'items_movimientos'
        
    def __str__(self):
        return f"Movimiento {self.id_movimiento} - {self.id_item.nombre_item}"
    
    
        