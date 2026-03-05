from django.shortcuts import render, redirect, get_object_or_404,get_list_or_404
from .models import Proyectos,Tareas,SubTareas,GestionSubtareas
from .forms import ProyectosForm, TareasForm, SubtareaForm, SubtareaEditForm, GestionSubtareaForm
from django.http.response import HttpResponse
# Create your views here.

from django.conf import settings
import os
import openpyxl

def main_seguimiento_actividades(request):
    proyectos = Proyectos.objects.all()
    if request.method == 'POST':
        proyecto_id =  request.POST.get('proyecto_seleccionado')        
        if proyecto_id:
            return redirect('ver_tareas',pk=proyecto_id)
    return render(request,'seguimiento_actividades/main.html',{'proyectos':proyectos})


def ver_tareas(request,pk):
    proyecto = Proyectos.objects.get(pk=pk)    
    tareas = Tareas.objects.filter(id_proyecto=pk)    
    subtareas = SubTareas.objects.filter(id_proyecto=pk)    
    return render(request,'seguimiento_actividades/tareas.html',{'tareas':tareas,'subtareas':subtareas,'proyecto':proyecto})


def agregar_proyecto(request):
    if request.method == 'POST':
        formulario_proyecto = ProyectosForm(request.POST)
        if formulario_proyecto.is_valid():            
            proyecto = formulario_proyecto.save()
            return redirect('agregar_tarea',pk=proyecto.id)
    else:
        formulario_proyecto = ProyectosForm()
    return render(request,'seguimiento_actividades/formulario_agregar_proyecto.html',{'formulario_proyecto':formulario_proyecto})


def agregar_tarea(request,pk):
    proyecto = Proyectos.objects.get(pk=pk)    
    if request.method == 'POST':
        formulario_tarea = TareasForm(request.POST)    
        if formulario_tarea.is_valid():
            tarea =  formulario_tarea.save(commit=False)
            tarea.id_proyecto = proyecto
            tarea.save()            
            return redirect('agregar_subtarea',pk=tarea.id)
    else:
        formulario_tarea = TareasForm()
    return render(request,'seguimiento_actividades/formulario_agregar_tarea.html',{'proyecto':proyecto,'formulario_tarea':formulario_tarea})

def agregar_subtarea(request,pk):
    tarea = Tareas.objects.get(pk=pk)    
    if request.method == 'POST':
        formulario_subtarea = SubtareaForm(request.POST)
        if formulario_subtarea.is_valid():
            subtarea = formulario_subtarea.save(commit=False)
            subtarea.id_proyecto = tarea.id_proyecto
            subtarea.id_tarea = tarea
            subtarea.save()
            
            return redirect(ver_tareas,pk=tarea.id_proyecto.id)
    else:
        formulario_subtarea = SubtareaForm()
    return render(request,'seguimiento_actividades/formulario_agregar_subtarea.html',{'tarea':tarea,'formulario_subtarea':formulario_subtarea})


def agregar_subtarea_seleccionada(request,pk):
    tareas_proyecto = Tareas.objects.filter(id_proyecto=pk)
    proyecto = Proyectos.objects.get(pk=pk)
    if request.method == 'POST':
        tarea_id = request.POST.get('tarea_seleccionada')
        if tarea_id:
            return redirect('agregar_subtarea',pk=tarea_id)
        
    return render(request,'seguimiento_actividades/listado_tareas_x_proyecto.html',{'tareas_proyecto':tareas_proyecto,'proyecto':proyecto})


def editar_subtarea(request,pk):
    sub_tarea = SubTareas.objects.get(pk=pk)
    if request.method == 'POST':
        formulario_subtarea = SubtareaEditForm(request.POST, instance=sub_tarea)
        if formulario_subtarea.is_valid():
            formulario_subtarea.save()
            return redirect('ver_tareas',pk=sub_tarea.id_proyecto)
    else:
        formulario_subtarea = SubtareaEditForm(instance=sub_tarea)
    return render(request,'seguimiento_actividades/formulario_editar_subtarea.html',{'formulario_subtarea':formulario_subtarea,'sub_tarea':sub_tarea})
            


def agregar_gestion(request,pk):
    subtarea = SubTareas.objects.get(pk=pk)
    if request.method == 'POST':
        formulario_gestion = GestionSubtareaForm(request.POST)
        if formulario_gestion.is_valid():
            gestion = formulario_gestion.save(commit=False)
            gestion.id_subtarea = subtarea
            gestion.save()
            return redirect('ver_listado_gestion',pk=subtarea.id)
    else:
        formulario_gestion = GestionSubtareaForm()
        
    return render(request,'seguimiento_actividades/formulario_agregar_gestion.html',{'formulario_gestion':formulario_gestion,'subtarea':subtarea})
        
        
def listar_gestion(request,pk):
    gestiones = GestionSubtareas.objects.filter(id_subtarea=pk)
    return render(request,'seguimiento_actividades/listar_gestion.html',{'gestiones':gestiones})


def imprimir_gestion(request,pk):
    gestion = GestionSubtareas.objects.get(id_subtarea=pk)
    plantilla_ruta = os.path.join(settings.MEDIA_ROOT,'formatos_excel','BITACORA_GESTION_PROYECTOS.xlsx')
    try:
        libro = openpyxl.load_workbook(plantilla_ruta)
        hoja = libro.active
    except FileNotFoundError:
        return HttpResponse("Error plantilla no encontrada")
    hoja['D5'] = str(gestion.id)
    hoja['D6'] = str(gestion.id_subtarea.id_proyecto.nombre_proyecto)
    hoja['D7'] = str(gestion.id_subtarea.id_tarea.detalle_tarea)
    hoja['D8'] = str(gestion.id_subtarea.detalle_subtarea)
    hoja['D9'] = str(gestion.id_subtarea.responsable_asignado.nombre)
    hoja['C10'] = str(gestion.id_subtarea.inicio_actividad)
    hoja['G10'] = str(gestion.id_subtarea.fin_actividad)
    hoja['B12'] = str(gestion.detalle_gestion)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=bitacora_numero_{str(gestion.id)}.xlsx'
    libro.save(response)
    return response