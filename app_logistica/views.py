from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse, FileResponse, Http404

#Login
from .forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import *
from django.db.models import Count,Exists,Q
from django.db import transaction

from datetime import datetime
from datetime import date

from utilidades.genera_qr import generar_qr

#PDF
import os
from django.conf import settings
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.core.files.base import ContentFile

def generar_pdf_movimiento(cabecera_id):
    cabecera = ItemMovimientosCabecera.objects.get(pk=cabecera_id)
    movimientos = ItemsMovimientos.objects.filter(id_movimiento_cabezera=cabecera)
    
    # 1. Renderizar el HTML
    context = {
        'cabecera': cabecera,
        'movimientos': movimientos,
        'logo_path': os.path.join(settings.STATIC_ROOT, 'incasur.png'), # Opcional
    }
    html_string = render_to_string('logistica/pdf_template_movimientos.html', context)
    
    # 2. Generar el PDF en memoria
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
    
    if not pdf.err:
        # 3. Guardar el PDF en el modelo
        nombre_archivo = f"movimiento_{cabecera.id_cabecera}.pdf"
        cabecera.pdf_archivo.save(nombre_archivo, ContentFile(result.getvalue()), save=True)
        return True
    return False

# Create your views here.
@login_required(login_url="login_logistica")
def logistica_items(request):
    items =  Items.objects.all()
    return render(request,'logistica/items.html',{'items':items})

@login_required(login_url="login_logistica")
def agregar_item_tipo_item(request):
    tipos_item = TipoItems.objects.all()    
    if request.method == 'POST':        
        tipo_item_seleccionado = request.POST.get('tipo_item')
        tipo_item = TipoItems.objects.get(pk=int(tipo_item_seleccionado))
        print("Hasta aqui esta bien")
        if tipo_item.id_tipo == 1:                
            return redirect('agregar_item_stock',pk=tipo_item.id_tipo)
        else:
            return redirect('seleccionar_proveedor')    
    return render(request,'logistica/seleccionar_tipo_item.html',{'tipos_item':tipos_item})

    
@login_required(login_url="login_logistica")
def agregar_item_stock(request,pk):
    tipo_item = TipoItems.objects.get(pk=pk)        
    if request.method == 'POST':
        form = ItemsFormStock(request.POST)
        if form.is_valid():
            form_item_stock = form.save(commit=False)
            form_item_stock.cantidad_items = 0
            form_item_stock.tipo_item = tipo_item                                  
            form_item_stock.save()                        
            qr_link = f"http://192.168.1.31:8000/logistica/informacion-articulo-stock/{form_item_stock.pk}"
            #qr_link = f"http://192.168.1.8/aplicaciones-incasur/logistica/editar-item-celular/{item.pk}"
            nombre_archivo_qr = generar_qr(form_item_stock.pk,qr_link)
            form_item_stock.imagen_qr.name = f"imagenes_qr/{nombre_archivo_qr}"
            form_item_stock.save()            
            return redirect ('logistica_items')
    else:
        form = ItemsFormStock()
        #form = ItemsFormStock(initial={'tipo_item':tipo_item})
    return render(request,'logistica/formulario_agregar_item_stock.html',{'form':form})


@login_required(login_url="login_logistica")
def agregar_item_serializable(request,pk):
    proveedor_seleccionado = Proveedores.objects.get(pk=pk)
    item_serialisable = TipoItems.objects.get(pk=2)
    if request.method == 'POST':
        form = ItemsFormSerializable(request.POST)
        if form.is_valid():
            form_item_serializable = form.save(commit=False)
            form_item_serializable.cantidad_items = 1
            form_item_serializable.tipo_item = item_serialisable
            form_item_serializable.proveedor = proveedor_seleccionado
            form_item_serializable.save()
            qr_link = f"http://192.168.1.31:8000/logistica/informacion-articulo-serializable-celular/{form_item_serializable.pk}"
            #qr_link = f"http://192.168.1.8/aplicaciones-incasur/logistica/editar-item-celular/{item.pk}"
            nombre_archivo_qr = generar_qr(form_item_serializable.pk,qr_link)
            form_item_serializable.imagen_qr.name = f"imagenes_qr/{nombre_archivo_qr}"
            form_item_serializable.save()   
            return redirect ('logistica_items')
    else:
        form = ItemsFormSerializable()   
    return render(request,'logistica/formulario_agregar_item_serializable.html',{'form':form})


@login_required(login_url="login_logistica")
def seleccionar_proveedor(request):
    return render(request,'logistica/seleccionar_proveedor.html')            


@login_required(login_url="login_logistica")
def seleccionar_item_mov(request,pk):    
    articulo = Items.objects.get(pk=pk)        
    origen = articulo.proveedor
    almacenes = Almacenes.objects.values_list('nombre_almacen', flat=True)
    colaboradores_activos = EstadoColaboradores.objects.get(pk=1)
    colaboradores_activos =  Colaboradores.objects.values_list('nombre_colaborador',flat=True).filter(estado_colaboradores=colaboradores_activos)    
    destinos = almacenes       
    return render(request,'logistica/opciones_movimientos_filtradas_ingreso_serial.html',{'articulo':articulo,'origen':origen,'destinos':destinos})


@login_required(login_url="login_logistica")
def seleccionar_proveedor_mov(request,pk):
    tipo_articulo_stock = TipoItems.objects.get(pk=1)
    proveedor = Proveedores.objects.get(pk=pk)
    articulos = Items.objects.all()
    articulos = Items.objects.filter(tipo_item=tipo_articulo_stock)    
    origen = proveedor
    destinos = Almacenes.objects.values_list('nombre_almacen', flat=True)    
    
    return render(request,'logistica/opciones_movimientos_filtradas_ingreso.html',{'proveedor':proveedor,'articulos':articulos,'origen':origen,'destinos':destinos})            


@login_required(login_url="login_logistica")
def buscar_proveedor(request):
    data_input = request.GET.get('ruc','').strip()
    proveedores_encontrados = Proveedores.objects.filter(documento__icontains=data_input)    
    return render(request,'logistica/resultado_busqueda_proveedor.html',{'proveedores_encontrados':proveedores_encontrados})

@login_required(login_url="login_logistica")
def buscar_proveedor_movimiento(request):
    data_input = request.GET.get('ruc','').strip()
    proveedores_encontrados = Proveedores.objects.filter(documento__icontains=data_input)    
    return render(request,'logistica/resultado_busqueda_proveedor_mov.html',{'proveedores_encontrados':proveedores_encontrados})

@login_required(login_url="login_logistica")
def buscar_item_movimiento(request):
    data_input = request.GET.get('nombre_item','').strip()
    tipo_item = TipoItems.objects.get(pk=2)
    items_filtrados = Items.objects.filter(nombre_item__icontains=data_input,tipo_item=tipo_item)    
    return render(request,'logistica/resultado_busqueda_item_mov.html',{'items_filtrados':items_filtrados})


@login_required(login_url="login_logistica")
def agregar_proveedor_stock(request):    
    if request.method == 'POST':
        form = ProveedoresForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('agregar_movimientos')
    else:
        form = ProveedoresForm()
    return render(request,'logistica/formulario_agregar_proveedor_stock.html',{'form':form})        

@login_required(login_url="login_logistica")
def agregar_proveedor_serializable(request):    
    if request.method == 'POST':
        form = ProveedoresForm(request.POST)
        if form.is_valid():
            proveedor_seleccionado = form.save()
            return redirect('agregar_item_serializable',pk=proveedor_seleccionado.id_proveedor)
    else:
        form = ProveedoresForm()
    return render(request,'logistica/formulario_agregar_proveedor.html',{'form':form})        


@login_required(login_url="login_logistica")
def editar_item_stock(request,pk):
    item = get_object_or_404(Items,pk=pk)
    #inventarios_historial = HistorialInventarios.objects.filter(id_item=pk)
    if request.method == 'POST':
        form = ItemsFormStock(request.POST,instance=item)
        if form.is_valid():
            form.save()
            return redirect('logistica_items')
    else:
        form = ItemsFormStock(instance=item)
    return render(request,'logistica/formulario_editar_item_stock.html',{'form':form,'item':item})


@login_required(login_url="login_logistica")
def editar_item_serializable(request,pk):
    item = get_object_or_404(Items,pk=pk)
    #inventarios_historial = HistorialInventarios.objects.filter(id_item=pk)
    if request.method == 'POST':
        form = ItemsFormSerializable(request.POST,instance=item)
        if form.is_valid():
            form.save()
            return redirect('logistica_items')
    else:
        form = ItemsFormSerializable(instance=item)
    return render(request,'logistica/formulario_editar_item_serializable.html',{'form':form,'item':item})
    


@login_required(login_url="login_logistica")
def informacion_articulo_stock(request,pk):            
    item = get_object_or_404(Items,pk=pk)    
    inventario = HistorialInventarios.objects.filter(id_item=pk)        
    return render(request,'logistica/ver_info_item_stock.html',{'item':item,'inventario':inventario})


@login_required(login_url="login_logistica")
def informacion_articulo_serializable(request,pk):            
    item = get_object_or_404(Items,pk=pk)    
    inventario = HistorialInventarios.objects.filter(id_item=pk)        
    return render(request,'logistica/ver_info_item_serializable.html',{'item':item,'inventario':inventario})


@login_required(login_url="login_logistica")
def informacion_articulo_serializable_celular(request,pk):            
    item = get_object_or_404(Items,pk=pk)    
    inventario = HistorialInventarios.objects.filter(id_item=pk)        
    return render(request,'logistica/ver_info_item_serializable_celular.html',{'item':item,'inventario':inventario})

    
@login_required(login_url='login_logistica')    
def inventariar_articulo(request,pk):
    articulo = get_object_or_404(Items,pk=pk)
    hoy = date.today()
    #area_nombre = (lambda valor: valor.nombre_area if valor is not None else "No Asignado")(articulo.id_area)
    almacen_nombre = (lambda valor: valor.nombre_almacen if valor is not None else "No Asignado")(articulo.id_almacen)
    usuario_nombre = (lambda valor: valor.nombre_colaborador if valor is not None else "No Asignado")(articulo.id_usuario)        
    if request.method == 'POST':        
        historial_inventario = HistorialInventarios()
        historial_inventario.id_item = articulo        
        historial_inventario.nombre_almacen = almacen_nombre
        historial_inventario.nombre_usuario = usuario_nombre
        historial_inventario_duplicado = HistorialInventarios.objects.filter(id_item=pk,fecha_modificacion__date=hoy)
        historial_inventario_duplicado.delete()
        historial_inventario.save()
        return redirect('logistica_items')
        
    return render(request,'logistica/confirmar_inventariar_articulo.html',{'articulo':articulo})
    
@login_required(login_url="login_logistica")    
def eliminar_articulo(request,pk):
    articulo = get_object_or_404(Items,pk=pk)                
    if articulo.id_almacen == None and articulo.id_usuario == None:
        if request.method == 'POST':
            articulo.delete()
            return redirect('logistica_items')
        return render(request,'logistica/confirmar_eliminar_articulo.html',{'articulo':articulo})        
    else:
        return render(request,'logistica/no_es_posible_eliminar.html',{'articulo':articulo})


@login_required(login_url='login_logistica')
def movimientos_articulo(request,pk):
    articulo = get_object_or_404(Items,pk=pk)
    movimientos = ItemsMovimientos.objects.filter(id_item=articulo)
    return render(request,'logistica/historial_inventario.html',{'movimientos':movimientos})
    
        
@login_required(login_url='login_logistica')
def historial_inventario_articulo(request,pk):
    articulo = get_object_or_404(Items,pk=pk)
    inventarios = HistorialInventarios.objects.filter(id_item=articulo)
    return render(request,'logistica/historial_inventario.html',{'inventarios':inventarios})
    
@login_required(login_url="login_logistica")
def logistica_almacenes(request):
    almacenes = Almacenes.objects.annotate(total_articulos=Count('items'))         
    return render(request,'logistica/almacenes.html',{'almacenes':almacenes})

@login_required(login_url="login_logistica")
def agregar_almacenes(request):
    if request.method == "POST":
        form = AlmacenesForm(request.POST)        
        if form.is_valid():
            form.save()
            return redirect('logistica_almacenes')                    
    else:
        form = AlmacenesForm()
    return render(request,'logistica/formulario_agregar_almacenes.html',{'form':form})

@login_required(login_url="login_logistica")
def editar_almacen(request,pk):
    almacen = get_object_or_404(Almacenes,pk=pk)
    if request.method == 'POST':
        form = AlmacenesForm(request.POST, instance=almacen)
        if form.is_valid():
            form.save()
        return redirect('logistica_almacenes')
    else:
        form = AlmacenesForm(instance=almacen)                
    return render(request,'logistica/formulario_editar_almacen.html',{'form':form})

@login_required(login_url="login_logistica")
def eliminar_almacen(request,pk):
    almacen = get_object_or_404(Almacenes,pk=pk)
    if request.method == 'POST':
        almacen.delete()
        return redirect('logistica_almacenes')        
    return render(request,'logistica/confirmar_eliminar_almacen.html',{'almacen':almacen})
        
@login_required(login_url="login_logistica")        
def items_por_almacen(request,pk):
    año = datetime.now().year
    inventario_anio_actual = HistorialInventarios.objects.filter(id_item=pk,fecha_modificacion__year=año)
        
    items = Items.objects.filter(id_almacen = pk).annotate(inventario_anio_actual=Exists(inventario_anio_actual))
    return render(request,'logistica/items.html',{'items':items})

@login_required(login_url="login_logistica")
def logistica_movimientos(request):
    movimientos = ItemsMovimientos.objects.select_related(
        'id_movimiento_cabezera', 
        'id_item',
        'tipo_movimiento'
    ).all().order_by('-fecha_modificacion')
    return render(request,'logistica/movimientos.html',{'movimientos':movimientos})

@login_required(login_url="login_logistica")
def movimientos_por_item(request,pk):
    movimientos = ItemsMovimientos.objects.select_related(
        'id_movimiento_cabezera', 
        'id_item',
        'tipo_movimiento'
    ).filter(id_item=pk).order_by('-fecha_modificacion')
    return render(request,'logistica/movimientos.html',{'movimientos':movimientos})


@login_required(login_url="login_logistica")    
def movimientos_por_colaborador(request,pk):
    colaborador = Colaboradores.objects.get(pk=pk)
    movimientos = ItemsMovimientos.objects.filter(Q(nombre_origen=colaborador.nombre_colaborador) | 
        Q(nombre_destino=colaborador.nombre_colaborador)
    )
    return render(request,'logistica/movimientos.html',{'movimientos':movimientos})

@login_required(login_url="login_logistica")
def imprimir_pdf_movimientos_firmado(request,pk):
    cabecera = get_object_or_404(ItemMovimientosCabecera,pk=pk)    
    if not cabecera.pdf_archivo:
        raise Http404("Archivo no Existe")
    response = FileResponse(cabecera.pdf_archivo.open('rb'), content_type='application/pdf')
    
    # Forzamos la descarga con el nombre que queramos
    nombre_archivo = f"Movimiento_Firmado_{cabecera.colaborador_confirma.nombre_colaborador}-{pk}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    
    return response

@login_required(login_url="login_logistica")
def imprimir_pdf_qrs(request):
    articulo_tipo_no_baja = TipoEstadoItems.objects.exclude(id_estado=3)
    tipo_articulo_serial = TipoItems.objects.get(id_tipo=2)    
    articulos = Items.objects.filter(tipo_item=tipo_articulo_serial,id_estado__in=articulo_tipo_no_baja)
        
    html_string = render_to_string('logistica/pdf_imprimir_qrs.html', {'articulos': articulos})
    
    # 2. Preparar el buffer
    result = BytesIO()
    
    # 3. Generar PDF con manejo de errores estricto
    pisa_status = pisa.CreatePDF(
        src=html_string,  # Pasamos el string directamente
        dest=result,
        encoding='utf-8'
    )
    
    # Si hay error en la generación, mostramos el error en texto en lugar de un PDF corrupto
    if pisa_status.err:
        return HttpResponse(f"Error técnico al generar PDF: {pisa_status.err}", status=500)

    # 4. Preparar respuesta
    pdf_final = result.getvalue() # Obtenemos los bytes directamente
    result.close() # Cerramos el buffer

    response = HttpResponse(pdf_final, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="TODOS_LOS_QR.pdf"'
    
    return response


@login_required(login_url="login_logistica")
@transaction.atomic
def agregar_movimientos(request):
    estado_colaborador_activo = EstadoColaboradores.objects.get(pk=1)
    colaboradores = Colaboradores.objects.filter(estado_colaboradores=estado_colaborador_activo)        
    tipos_movimiento = TiposMovimiento.objects.all()
    movimientos = ItemsMovimientos.objects.all()
    cabecera_id = ""
    if request.method == 'POST':
        colaborador_id = request.POST.get('colaborador_id')
        firma_data = request.POST.get('firma_base64')
        items_ids = request.POST.getlist('items_ids[]')
        vouchers = request.POST.getlist('items_voucher[]')
        referencia = request.POST.getlist('items_referencia[]')
        factura = request.POST.getlist('items_factura[]')
        fecha_contable = request.POST.getlist('items_fechacontable[]')
        items_tipo_movimiento = request.POST.getlist('items_tipo_movimiento[]')
        items_origen = request.POST.getlist('items_origen[]')
        items_destino = request.POST.getlist('items_destino[]')
        cantidades = request.POST.getlist('cantidades[]')        
        items_mov_ref = request.POST.getlist('items_mov_ref[]')        
        items_observaciones = request.POST.getlist('items_observaciones[]')
        if not items_ids:
            return HttpResponse("Debe agregar al menos un ítem", status=400)
        colaborador = get_object_or_404(Colaboradores, pk=colaborador_id)
        cabecera = ItemMovimientosCabecera(
            colaborador_confirma=colaborador,
            firma_base64=firma_data
        )
        cabecera.save()        
        cabecera_id = cabecera.id_cabecera
        for i_id,i_vouch,i_refe,i_fact,fecha_cnt,i_tip_mov,i_ori,i_des,cant,obs,i_mov_ref in zip(items_ids,vouchers,referencia,factura,fecha_contable,items_tipo_movimiento,items_origen,items_destino, cantidades,items_observaciones,items_mov_ref):
            articulo = Items.objects.select_for_update().get(pk=i_id)            
            tipos_movimiento = TiposMovimiento.objects.get(id_tipo=int(i_tip_mov))             
            i_fe_cnt = datetime.strptime(fecha_cnt, '%Y-%m-%d').date()
            if not i_vouch or i_vouch == '':
                i_vouch = None 
            if not i_refe or i_refe == '':
                i_refe = None 
            if not i_vouch or i_vouch == '':
                i_vouch = None 
            if not i_fact or i_fact == '':
                i_fact = None                        
            if not i_fe_cnt or i_fe_cnt == '':
                i_fe_cnt = None
            if not i_mov_ref or i_mov_ref == '':
                i_mov_ref = None                
            else:
                i_mov_ref = ItemsMovimientos.objects.filter(id_movimiento=i_mov_ref).first()            
            # Bloqueo de fila para evitar errores de concurrencia
            cant = int(cant)
            if i_tip_mov == "1":                
                almacen = Almacenes.objects.get(nombre_almacen=i_des) 
                ItemsMovimientos.objects.create(
                    id_movimiento_cabezera=cabecera,
                    id_item=articulo,
                    voucher=i_vouch,
                    referencia=i_refe,                    
                    fecha_contable=i_fe_cnt,
                    factura=i_fact,
                    tipo_movimiento=tipos_movimiento,
                    nombre_origen=i_ori, # O el que definas
                    nombre_destino=i_des,
                    cantidad_movimiento=cant,
                    id_movimiento_referencia=i_mov_ref,                    
                    observaciones=obs
                )
                articulo.id_almacen = almacen               
                articulo.cantidad_items += cant
                articulo.save()                                    
            elif i_tip_mov == "2":
                colaborador = get_object_or_404(Colaboradores,nombre_colaborador=i_des )
                if articulo.cantidad_items >= cant:
                    ItemsMovimientos.objects.create(
                        id_movimiento_cabezera=cabecera,
                        id_item=articulo,
                        voucher=i_vouch,
                        referencia=i_refe,                    
                        fecha_contable=i_fe_cnt,
                        factura=i_fact,
                        tipo_movimiento=tipos_movimiento,
                        nombre_origen=i_ori, # O el que definas
                        nombre_destino=i_des,
                        cantidad_movimiento=cant,
                        id_movimiento_referencia=i_mov_ref,                    
                        observaciones=obs
                    )
                    articulo.id_usuario = colaborador
                    articulo.id_almacen = None
                    if articulo.tipo_item.nombre_tipo.lower() == 'stock':                        
                        articulo.cantidad_items -= cant
                    else:
                        articulo.cantidad_items = 1
                    articulo.save()
                else:
                    raise Exception(f"Stock Modificado en ultimo Momento, No se Guardo el Movimiento {articulo.nombre_item}")            
            elif i_tip_mov == "3":
                almacen = Almacenes.objects.get(nombre_almacen=i_des)                
                ItemsMovimientos.objects.create(
                    id_movimiento_cabezera=cabecera,
                    id_item=articulo,
                    voucher=i_vouch,
                    referencia=i_refe,                    
                    fecha_contable=i_fe_cnt,
                    factura=i_fact,
                    tipo_movimiento=tipos_movimiento,
                    nombre_origen=i_ori, # O el que definas
                    nombre_destino=i_des,
                    cantidad_movimiento=cant,
                    id_movimiento_referencia=i_mov_ref,                    
                    observaciones=obs
                )
                articulo.id_usuario = None
                articulo.id_almacen = almacen
                if articulo.tipo_item.nombre_tipo.lower() == 'stock':                        
                    articulo.cantidad_items += cant
                else:
                    articulo.cantidad_items = 1
                articulo.save()                
            elif i_tip_mov == "4":
                #if articulo.cantidad_items >= cant:
                ItemsMovimientos.objects.create(
                    id_movimiento_cabezera=cabecera,
                    id_item=articulo,
                    voucher=i_vouch,
                    referencia=i_refe,                    
                    fecha_contable=i_fe_cnt,
                    factura=i_fact,
                    tipo_movimiento=tipos_movimiento,
                    nombre_origen=i_ori, # O el que definas
                    nombre_destino=i_des,
                    cantidad_movimiento=cant,
                    id_movimiento_referencia=i_mov_ref,                    
                    observaciones=obs
                )
                articulo.cantidad_items = cant
                articulo.save()
                #else:
                    #raise Exception(f"Stock Modificado en ultimo Momento, No se Guardo el Movimiento {articulo.nombre_item}")            
            elif i_tip_mov == "5":
                estado_debaja = TipoEstadoItems.objects.get(pk=2)
                if articulo.cantidad_items >= cant:
                    ItemsMovimientos.objects.create(
                        id_movimiento_cabezera=cabecera,
                        id_item=articulo,
                        voucher=i_vouch,
                        referencia=i_refe,                    
                        fecha_contable=i_fe_cnt,
                        factura=i_fact,
                        tipo_movimiento=tipos_movimiento,
                        nombre_origen=i_ori, # O el que definas
                        nombre_destino=i_des,
                        cantidad_movimiento=cant,
                        id_movimiento_referencia=i_mov_ref,                    
                        observaciones=obs
                    )
                    #articulo.id_usuario = None                    
                    #articulo.id_almacen = None
                    articulo.id_estado = estado_debaja
                    articulo.cantidad_items = cant
                    articulo.save()
                else:
                    raise Exception(f"Stock Modificado en ultimo Momento, No se Guardo el Movimiento {articulo.nombre_item}")            
            elif i_tip_mov == "6":
                if articulo.cantidad_items >= cant:
                    ItemsMovimientos.objects.create(
                        id_movimiento_cabezera=cabecera,
                        id_item=articulo,
                        voucher=i_vouch,
                        referencia=i_refe,                    
                        fecha_contable=i_fe_cnt,
                        factura=i_fact,
                        tipo_movimiento=tipos_movimiento,
                        nombre_origen=i_ori, # O el que definas
                        nombre_destino=i_des,
                        cantidad_movimiento=cant,
                        id_movimiento_referencia=i_mov_ref,                    
                        observaciones=obs
                    )                                        
                    articulo.cantidad_items = cant
                    articulo.save()
                else:
                    raise Exception(f"Stock Modificado en ultimo Momento, No se Guardo el Movimiento {articulo.nombre_item}")            
            elif i_tip_mov == "7":
                if articulo.cantidad_items >= cant:
                    ItemsMovimientos.objects.create(
                        id_movimiento_cabezera=cabecera,
                        id_item=articulo,
                        voucher=i_vouch,
                        referencia=i_refe,                    
                        fecha_contable=i_fe_cnt,
                        factura=i_fact,
                        tipo_movimiento=tipos_movimiento,
                        nombre_origen=i_ori, # O el que definas
                        nombre_destino=i_des,
                        cantidad_movimiento=cant,
                        id_movimiento_referencia=i_mov_ref,                    
                        observaciones=obs
                    )                                    
                    articulo.cantidad_items = cant
                    articulo.save()
                else:
                    raise Exception(f"Stock Modificado en ultimo Momento, No se Guardo el Movimiento {articulo.nombre_item}")            
            else:
                raise Exception(f"Ubo un error No Finalizo correctamente {articulo.nombre_item}")
            
        generar_pdf_movimiento(cabecera_id)                     
        return redirect('logistica_movimientos')
                        
    return render(request,'logistica/formulario_agregar_movimiento.html',{'colaboradores':colaboradores,'tipos_movimiento':tipos_movimiento,'movimientos':movimientos})


@login_required(login_url="login_logistica")
def agregar_fila_item(request):
    voucher = request.POST.get('voucher','')
    referencia = request.POST.get('referencia','')
    factura = request.POST.get('factura','')
    fecha_contable = request.POST.get('fecha_contable','')
    movimiento = request.POST.get('tipo_movimiento')
    observaciones = request.POST.get('observaciones')
    origen = request.POST.get('origen')
    destino = request.POST.get('destino')
    item_id = request.POST.get('articulo')
    mov_ref = request.POST.get('mov_ref')
    tipo_movimiento = get_object_or_404(TiposMovimiento,pk=movimiento)
    cantidad = int(request.POST.get('cantidad', 1))
    articulo = get_object_or_404(Items, pk=item_id)
    if cantidad < 0:
            return HttpResponse(f'<script>alert("No se Permite un ingreso Negativo");</script>', status=200)        
    if movimiento == "2":
        voucher = articulo.comprobante_contable
        fecha_contable = articulo.fecha_contable
        factura = articulo.factura_boleta                
        if articulo.cantidad_items < cantidad:
            return HttpResponse(f'<script>alert("Stock insuficiente para {articulo.nombre_item}");</script>', status=200)
    if movimiento == "3":
        voucher = articulo.comprobante_contable
        fecha_contable = articulo.fecha_contable
        factura = articulo.factura_boleta
        if mov_ref == "":
            return HttpResponse(f'<script>alert("Debe Elegir un Movimiento Referencia");</script>', status=200)
    if movimiento == "4":
        if observaciones == "":
            return HttpResponse(f'<script>alert("Debe Colocar el Motivo de Ajuste");</script>', status=200)
    if movimiento == "5":
        voucher = articulo.comprobante_contable
        fecha_contable = articulo.fecha_contable
        factura = articulo.factura_boleta
        if observaciones == "":
            return HttpResponse(f'<script>alert("Debe Colocar el Motivo de Baja");</script>', status=200)
    if movimiento == "6":
        if mov_ref == "":
            return HttpResponse(f'<script>alert("Debe Elegir un Movimiento Referencia");</script>', status=200)        
    if movimiento == "7":
        voucher = articulo.comprobante_contable
        fecha_contable = articulo.fecha_contable
        factura = articulo.factura_boleta        
        if articulo.cantidad_items < cantidad:
            return HttpResponse(f'<script>alert("Stock insuficiente para {articulo.nombre_item}");</script>', status=200)
    # Validación de stock en el servidor
    

    context = {
        'fecha_contable':fecha_contable,
        'voucher':voucher,
        'referencia':referencia,
        'factura':factura,
        'articulo': articulo,
        'tipo_movimiento':tipo_movimiento,
        'origen':origen,
        'destino': destino,
        'cantidad': cantidad,
        'mov_ref':mov_ref,
        'observaciones':observaciones
        }
    # Retorna solo el fragmento de la fila
    return render(request, 'logistica/parcial_fila_item.html', context)

@login_required(login_url="login_logistica")
def filtrar_campos_movimientos(request):
    movimientos = request.POST.get('tipo_movimiento')
    context = {}
    articulo_tipo_no_baja = TipoEstadoItems.objects.exclude(id_estado=2)
    tipo_articulo_stock = TipoItems.objects.get(id_tipo=1)
    tipo_articulo_serial = TipoItems.objects.get(id_tipo=2)    
    colaboradores_activos = EstadoColaboradores.objects.get(codigo_estado=1)
    if movimientos == "1":       
        return render(request,'logistica/seleccionar_proveedor_movimientos.html')
    elif movimientos == "2":
        articulos = Items.objects.filter(id_estado__in=articulo_tipo_no_baja,id_usuario__isnull=True)
        almacenes = Almacenes.objects.values_list('nombre_almacen', flat=True)
        colaboradores_activos =  Colaboradores.objects.values_list('nombre_colaborador',flat=True).filter(estado_colaboradores=colaboradores_activos)
        origenes = almacenes
        destinos = list(almacenes) + list(colaboradores_activos)
        mov_refs = ItemsMovimientos.objects.all()
        context={
            'articulos':articulos,
            'origenes':origenes,
            'destinos':destinos,
            'mov_refs':mov_refs,
        }
    elif movimientos == "3":
        articulos = Items.objects.filter(id_estado__in=articulo_tipo_no_baja,id_almacen__isnull=True)
        almacenes = Almacenes.objects.values_list('nombre_almacen', flat=True)
        colaboradores_activos =  Colaboradores.objects.values_list('nombre_colaborador',flat=True).filter(estado_colaboradores=colaboradores_activos)
        origenes = list(almacenes) + list(colaboradores_activos)
        destinos = almacenes
        mov_refs = ItemsMovimientos.objects.filter(tipo_movimiento=2)
        context={
            'articulos':articulos,
            'origenes':origenes,
            'destinos':destinos,
            'mov_refs':mov_refs,
        }
    elif movimientos == "4":
        articulos = Items.objects.filter(tipo_item=tipo_articulo_stock,id_estado__in=articulo_tipo_no_baja,id_almacen__isnull=False)
        almacenes = Almacenes.objects.values_list('nombre_almacen', flat=True)
        colaboradores_activos =  Colaboradores.objects.values_list('nombre_colaborador',flat=True).filter(estado_colaboradores=colaboradores_activos)
        origenes = almacenes
        destinos = almacenes
        mov_refs = ItemsMovimientos.objects.all()
        context={
            'articulos':articulos,
            'origenes':origenes,
            'destinos':destinos,
            'mov_refs':mov_refs,
        }
    elif movimientos == "5":
        articulos = Items.objects.filter(tipo_item=tipo_articulo_serial,id_estado__in=articulo_tipo_no_baja,id_almacen__isnull=False)
        almacenes = Almacenes.objects.values_list('nombre_almacen', flat=True)
        colaboradores_activos =  Colaboradores.objects.values_list('nombre_colaborador',flat=True).filter(estado_colaboradores=colaboradores_activos)
        origenes = almacenes
        destinos = ['Fin de Vida Util']
        mov_refs = ItemsMovimientos.objects.filter(tipo_movimiento=3)
        context={
            'articulos':articulos,
            'origenes':origenes,
            'destinos':destinos,
            'mov_refs':mov_refs,
        }
    elif movimientos == "6":
        articulos = Items.objects.filter(tipo_item=tipo_articulo_stock,id_estado__in=articulo_tipo_no_baja,id_usuario__insull=False)
        almacenes = Almacenes.objects.values_list('nombre_almacen', flat=True)
        colaboradores_activos =  Colaboradores.objects.values_list('nombre_colaborador',flat=True).filter(estado_colaboradores=colaboradores_activos)
        origenes = colaboradores_activos
        destinos = ['Consumido Totalmente']
        mov_refs = ItemsMovimientos.objects.filter(tipo_movimiento=2)
        context={
            'articulos':articulos,
            'origenes':origenes,
            'destinos':destinos,
            'mov_refs':mov_refs,
        }
    elif movimientos == "7":
        return render(request,'logistica/seleccionar_items_movimientos.html')
    return render(request,'logistica/opciones_movimientos_filtradas.html',context)        

@login_required(login_url="login_logistica")
def logistica_historial_inventario(request):
    inventarios = HistorialInventarios.objects.all()
    return render(request,'logistica/historial_inventario.html',{'inventarios':inventarios})

@login_required(login_url="login_logistica")
def articulos_no_inventariados(request):
    articulo_tipo_no_baja = TipoEstadoItems.objects.exclude(id_estado=1)        
    año = datetime.now().year
    inventarios_id = HistorialInventarios.objects.filter(fecha_modificacion__year=año).values_list('id_item',flat=True)    
    articulos = Items.objects.filter(id_estado__in=articulo_tipo_no_baja).exclude(id_item__in=inventarios_id)
    return render(request,'logistica/no_inventariados.html',{'articulos':articulos,'año':año})

@login_required(login_url="login_logistica")
def logistica_colaboradores(request):
    estado_colaborador_activo = EstadoColaboradores.objects.get(pk=1)
    colaboradores = Colaboradores.objects.filter(estado_colaboradores=estado_colaborador_activo)    
    items_colaborador = Items.objects.filter(id_usuario__in=colaboradores)
    return render(request,'logistica/colaboradores.html',{'colaboradores':colaboradores,'items_colaborador':items_colaborador})

@login_required(login_url="login_logistica")
def filtrar_colaboradores(request):
    colaborador_pista = request.GET.get('colaborador','').strip()
    colaboradores = Colaboradores.objects.filter(nombre_colaborador__icontains=colaborador_pista)
    items_colaborador = Items.objects.filter(id_usuario__in=colaboradores)
    return render(request,'logistica/colaboradores_filtrados.html',{'colaboradores':colaboradores,'items_colaborador':items_colaborador})


def login_logistica(request):
    if request.user.is_authenticated:
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('logistica_items')
    else:
        if request.method == 'POST':
            form = Login_Formulario(request.POST or None)
            if form.is_valid():
                data = form.cleaned_data
                usuario = data['usuario']
                contraseña = data['password']
                user = authenticate(request,username=usuario,password=contraseña)
                if user is not None:
                    login(request,user)
                    next_url = request.POST.get('next') or request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    else:
                        return redirect('logistica_items')        
                else:
                    messages.warning(request,"Usuario o Contraseña Incorrectos")
        else:
            form =  Login_Formulario()
        return render(request,'logistica/login.html',{'form':form})

@login_required(login_url="login_logistica")
def logout_logistica(request):
    logout(request)
    return redirect('login_logistica')