import json
import re
from datetime import time

from django.test import TestCase
from django.urls import reverse

from .models import DatosClinica, Horario, SolicitudCita, Testimonio, Tratamiento
from .views import agrupar_horarios


class AgruparHorariosTest(TestCase):
    def setUp(self):
        # La migración 0002 ya sembró la semana; estas pruebas arman la suya.
        Horario.objects.all().delete()

    def crear_semana(self):
        for dia in range(5):
            Horario.objects.create(dia=dia, abre=time(8, 0), cierra=time(18, 0))
        Horario.objects.create(dia=5, abre=time(8, 0), cierra=time(14, 0))
        Horario.objects.create(dia=6, cerrado=True)

    def test_los_dias_seguidos_con_la_misma_franja_se_juntan(self):
        self.crear_semana()
        grupos = agrupar_horarios(Horario.objects.all())

        self.assertEqual(len(grupos), 3)
        self.assertEqual(grupos[0]['etiqueta'], 'Lunes a viernes')
        self.assertEqual(grupos[0]['franja'], '8:00 – 18:00')
        self.assertEqual(grupos[1]['etiqueta'], 'Sábado')
        self.assertEqual(grupos[2]['etiqueta'], 'Domingo')
        self.assertTrue(grupos[2]['cerrado'])

    def test_dos_dias_seguidos_se_unen_con_y(self):
        Horario.objects.create(dia=0, abre=time(9, 0), cierra=time(17, 0))
        Horario.objects.create(dia=1, abre=time(9, 0), cierra=time(17, 0))
        grupos = agrupar_horarios(Horario.objects.all())
        self.assertEqual(grupos[0]['etiqueta'], 'Lunes y martes')

    def test_dias_no_consecutivos_no_se_juntan(self):
        Horario.objects.create(dia=0, abre=time(8, 0), cierra=time(18, 0))
        Horario.objects.create(dia=2, abre=time(8, 0), cierra=time(18, 0))
        grupos = agrupar_horarios(Horario.objects.all())
        self.assertEqual(len(grupos), 2)


class TratamientoTest(TestCase):
    def setUp(self):
        # Las zonas son únicas y la migración ya las ocupó todas.
        Tratamiento.objects.all().delete()

    def test_los_dientes_salen_de_la_zona(self):
        t = Tratamiento.objects.create(nombre='Ortodoncia', zona='caninos', descripcion='x')
        self.assertEqual(t.dientes, [13, 23])

    def test_la_encia_no_tiene_dientes(self):
        t = Tratamiento.objects.create(nombre='Periodoncia', zona='encia', descripcion='x')
        self.assertEqual(t.dientes, [])

    def test_un_tratamiento_sin_zona_no_tiene_dientes(self):
        t = Tratamiento.objects.create(nombre='Sedación', zona='', descripcion='x')
        self.assertEqual(t.dientes, [])

    def test_dos_tratamientos_no_pueden_compartir_zona(self):
        Tratamiento.objects.create(nombre='Limpieza', zona='molares', descripcion='x')
        with self.assertRaises(Exception):
            Tratamiento.objects.create(nombre='Otro', zona='molares', descripcion='x')

    def test_varios_tratamientos_pueden_quedarse_sin_zona(self):
        Tratamiento.objects.create(nombre='Odontopediatría', zona='', descripcion='x')
        Tratamiento.objects.create(nombre='Sedación', zona='', descripcion='x')
        self.assertEqual(Tratamiento.objects.sin_zona().count(), 2)


class DatosClinicaTest(TestCase):
    def test_cargar_siempre_devuelve_la_misma_fila(self):
        primero = DatosClinica.cargar()
        segundo = DatosClinica.cargar()
        self.assertEqual(primero.pk, segundo.pk)
        self.assertEqual(DatosClinica.objects.count(), 1)

    def test_guardar_fija_la_clave_en_uno(self):
        DatosClinica.objects.all().delete()
        datos = DatosClinica(pk=99, direccion='A', whatsapp='573007711549')
        datos.save()
        self.assertEqual(datos.pk, 1)
        self.assertEqual(DatosClinica.objects.count(), 1)

    def test_el_whatsapp_se_muestra_legible(self):
        datos = DatosClinica(whatsapp='573007711549')
        self.assertEqual(datos.whatsapp_legible, '+57 300 771 1549')

    def test_la_presentacion_se_parte_en_parrafos(self):
        datos = DatosClinica(presentacion='Uno.\n\nDos.\n\n\nTres.')
        self.assertEqual(datos.parrafos_presentacion, ['Uno.', 'Dos.', 'Tres.'])


class PaginaTest(TestCase):
    """La migración 0002 ya dejó el contenido cargado."""

    def test_la_pagina_responde(self):
        respuesta = self.client.get(reverse('sitio:inicio'))
        self.assertEqual(respuesta.status_code, 200)

    def test_muestra_los_tratamientos_con_su_zona(self):
        respuesta = self.client.get(reverse('sitio:inicio'))
        contenido = respuesta.content.decode()
        self.assertIn('data-tx="molares"', contenido)
        self.assertIn('Limpieza dental', contenido)
        self.assertIn('Odontología bajo sedación', contenido)

    def test_los_datos_estructurados_son_json_valido(self):
        respuesta = self.client.get(reverse('sitio:inicio'))
        bruto = re.search(
            r'<script type="application/ld\+json">(.*?)</script>',
            respuesta.content.decode(), re.DOTALL,
        )
        self.assertIsNotNone(bruto, 'no se encontró el bloque ld+json')

        ficha = json.loads(bruto.group(1))
        self.assertEqual(ficha['@type'], 'Dentist')
        self.assertEqual(ficha['address']['addressLocality'], 'Envigado')
        # El domingo está cerrado y no debe aparecer como franja.
        self.assertEqual(len(ficha['openingHoursSpecification']), 2)
        self.assertEqual(len(ficha['availableService']), 8)

    def test_los_datos_estructurados_siguen_siendo_validos_sin_horarios(self):
        Horario.objects.all().delete()
        respuesta = self.client.get(reverse('sitio:inicio'))
        bruto = re.search(
            r'<script type="application/ld\+json">(.*?)</script>',
            respuesta.content.decode(), re.DOTALL,
        )
        json.loads(bruto.group(1))

    def test_el_resumen_de_horario_no_deja_separadores_sueltos(self):
        respuesta = self.client.get(reverse('sitio:inicio'))
        resumen = respuesta.context['resumen_horario']
        self.assertEqual(resumen, 'Lunes a viernes 8:00 – 18:00 · Sábado 8:00 – 14:00')
        self.assertFalse(resumen.strip().endswith('·'))
        self.assertNotIn('Domingo', resumen)

    def test_la_seccion_de_sedacion_pasa_a_una_columna_sin_testimonios(self):
        contenido = self.client.get(reverse('sitio:inicio')).content.decode()
        self.assertIn('sedation__inner--solo', contenido)

        Testimonio.objects.create(texto='Muy bien', autor='Ana G.', publicado=True)
        contenido = self.client.get(reverse('sitio:inicio')).content.decode()
        self.assertNotIn('sedation__inner--solo', contenido)

    def test_solo_se_publican_los_testimonios_marcados(self):
        Testimonio.objects.create(texto='Visible', autor='Ana G.', publicado=True)
        Testimonio.objects.create(texto='Oculto', autor='Luis P.', publicado=False)
        contenido = self.client.get(reverse('sitio:inicio')).content.decode()
        self.assertIn('Visible', contenido)
        self.assertNotIn('Oculto', contenido)

    def test_un_tratamiento_sin_publicar_no_aparece(self):
        Tratamiento.objects.filter(nombre='Ortodoncia').update(publicado=False)
        contenido = self.client.get(reverse('sitio:inicio')).content.decode()
        self.assertNotIn('data-tx="caninos"', contenido)


class SolicitudCitaTest(TestCase):
    def datos_validos(self, **extra):
        datos = {'nombre': 'Ana Gómez', 'telefono': '3001234567', 'mensaje': 'Me da miedo'}
        datos.update(extra)
        return datos

    def test_una_solicitud_valida_se_guarda_y_redirige(self):
        respuesta = self.client.post(reverse('sitio:inicio'), self.datos_validos())
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(SolicitudCita.objects.count(), 1)
        self.assertEqual(SolicitudCita.objects.get().nombre, 'Ana Gómez')

    def test_un_telefono_muy_corto_se_rechaza(self):
        respuesta = self.client.post(reverse('sitio:inicio'), self.datos_validos(telefono='123'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(SolicitudCita.objects.count(), 0)

    def test_el_campo_trampa_descarta_el_envio(self):
        respuesta = self.client.post(
            reverse('sitio:inicio'), self.datos_validos(apellido='spam'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(SolicitudCita.objects.count(), 0)

    def test_el_mensaje_es_opcional(self):
        self.client.post(reverse('sitio:inicio'), self.datos_validos(mensaje=''))
        self.assertEqual(SolicitudCita.objects.count(), 1)

    def test_se_puede_elegir_un_tratamiento(self):
        tratamiento = Tratamiento.objects.get(nombre='Ortodoncia')
        self.client.post(
            reverse('sitio:inicio'), self.datos_validos(tratamiento=tratamiento.pk))
        self.assertEqual(SolicitudCita.objects.get().tratamiento, tratamiento)
