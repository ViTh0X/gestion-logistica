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
        fields = ['nombre_item','tipo_item','cantidad_items','id_area','id_estado']
        
                
class TipoItemForm(forms.ModelForm):
    
    class Meta:
        model = TipoItems
        fields = ['nombre_tipo']


    
    