from django.urls import path
from . import views

urlpatterns = [
    path('',views.main_seguimiento_actividades,name='main_seguimiento_actividades'),
]