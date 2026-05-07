from django.contrib import admin

# Register your models here.
from .models import CargoColaboradores,EstadoColaboradores,Colaboradores,TipoEstadoItems,TipoItems,TipoMoneda,TiposInsumo,TiposMovimiento


admin.site.register(CargoColaboradores)
admin.site.register(EstadoColaboradores)
admin.site.register(Colaboradores)
admin.site.register(TipoEstadoItems)
admin.site.register(TipoItems)
admin.site.register(TipoMoneda)
admin.site.register(TiposInsumo)
admin.site.register(TiposMovimiento)
