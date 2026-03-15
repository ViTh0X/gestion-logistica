from django import forms
from .models import *
#from django.forms import PasswordInput

class Login_Formulario(forms.Form):
    usuario = forms.CharField(required=True,widget=forms.TextInput(attrs={'autocomplete':'off'}))
    password = forms.CharField(required=True,widget=forms.PasswordInput(attrs={'autocomplete':'off'}))


class AlmacenesForm(forms.ModelForm):
    
    class Meta:
        model = Almacenes
        fields = ['nombre_almacen','descripcion_almacen','direccion_almacen']
    
class ItemsFormStock(forms.ModelForm):
    
    class Meta:
        model = Items
        fields = ['nombre_item','tipo_moneda','precio_unitario']
        widgets = {
            'precio_unitario': forms.NumberInput(attrs={
                'step':'0.01',
                'min':'0.00'                
            })
        }

class ItemsFormSerializable(forms.ModelForm):
    
    class Meta:
        model = Items
        fields = ['comprobante_contable','factura_boleta','fecha_contable','nombre_item','marca_item','modelo_item','serie_item','tipo_moneda','precio_unitario','id_estado']
        widgets = {
            'precio_unitario': forms.NumberInput(attrs={
                'step':'0.01',
                'min':'0.00'}
            ),
            'fecha_contable': forms.DateInput(
                format='%d-%m-%Y',
                attrs={
                    'type':'date'
                }
            )
        }
        
class ProveedoresForm(forms.ModelForm)            :
    
    class Meta:
        model = Proveedores
        fields = ['documento','nombre']


    
    