# Create your tests here.
from django.test import TestCase
from .models import CargoColaboradores, EstadoColaboradores, Colaboradores

class ColaboradoresTest(TestCase):
    def setUp(self):
        # 1. Creamos las dependencias necesarias (Foreign Keys)
        self.cargo = CargoColaboradores.objects.create(nombre_cargo="Administrador")
        self.estado = EstadoColaboradores.objects.create(nombre_estado="Activo")

    def test_creacion_colaborador(self):
        # 2. Intentamos crear el colaborador
        colaborador = Colaboradores.objects.create(
            nombre_colaborador="Leonard Quispe",
            usuario_sistema="lquispe",
            correo="leonard@example.com",
            usuario_sentinel="sent123",
            usuario_sbs="sbs456",
            usuario_windows="win789",
            usuario_reloj_control="reloj001",
            codigo_impresion_colaborador="IMP-001",
            cargo_colaborador=self.cargo,
            estado_colaboradores=self.estado
        )

        # 3. Validaciones (Assertions)
        self.assertEqual(colaborador.nombre_colaborador, "Leonard Quispe")
        self.assertEqual(colaborador.cargo_colaborador.nombre_cargo, "Administrador")
        self.assertTrue(Colaboradores.objects.filter(usuario_sistema="lquispe").exists())
        
        print("\n[PRUEBA UNITARIA] Colaborador creado y relacionado con éxito.")