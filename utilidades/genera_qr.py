import qrcode
from PIL import Image
from django.conf import settings
import os

def generar_qr(id_objeto,qr_link):
    nombre_archivo = f"{id_objeto}.png"
    ruta = os.path.join(settings.MEDIA_ROOT,'imagenes_qr')    
    qr_big = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr_big.add_data(qr_link)
    qr_big.make()
    imagen_qr = qr_big.make_image().convert('RGB')
    ruta_final = os.path.join(ruta,nombre_archivo)
    imagen_qr.save(ruta_final)
    
    return nombre_archivo
    
