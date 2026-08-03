"""Contenido real de la clínica, tomado del sitio anterior y de Instagram.

Va como migración de datos para que un despliegue nuevo arranque con la
página completa y no con una plantilla vacía. Todo esto es editable desde
el administrador; aquí solo está el punto de partida.
"""

from datetime import time

from django.db import migrations

TRATAMIENTOS = [
    {
        'nombre': 'Blanqueamiento y diseño de sonrisa',
        'zona': 'incisivos',
        'zona_detalle': 'Incisivos',
        'orden': 1,
        'descripcion': (
            'Los dientes que se ven cuando hablas. Aquí se trabaja color y forma: '
            'blanqueamiento, carillas y cierre de espacios entre dientes.'
        ),
    },
    {
        'nombre': 'Ortodoncia',
        'zona': 'caninos',
        'zona_detalle': 'Caninos',
        'orden': 2,
        'descripcion': (
            'El canino guía la mordida: cuando no encaja donde debe, el resto de los '
            'dientes se acomodan mal para compensar. Brackets o alineadores, según tu caso.'
        ),
    },
    {
        'nombre': 'Rehabilitación oral',
        'zona': 'premolares',
        'zona_detalle': 'Premolares',
        'orden': 3,
        'descripcion': (
            'Donde se reparte la fuerza al masticar, y donde primero se nota un diente '
            'fracturado. Se reconstruye lo que se dañó o se perdió: coronas, '
            'incrustaciones y prótesis.'
        ),
    },
    {
        'nombre': 'Limpieza dental',
        'zona': 'molares',
        'zona_detalle': 'Molares',
        'orden': 4,
        'descripcion': (
            'El sarro se acumula primero por fuera de los molares de arriba, justo donde '
            'desemboca la glándula salival. Por eso, aunque cepilles bien, esa zona '
            'necesita limpieza profesional.'
        ),
    },
    {
        'nombre': 'Cirugía maxilofacial',
        'zona': 'cordales',
        'zona_detalle': 'Cordales',
        'orden': 5,
        'descripcion': (
            'Las muelas del juicio y lo que no todos los consultorios manejan: '
            'extracciones complejas, dientes incluidos y cirugía de los maxilares.'
        ),
    },
    {
        'nombre': 'Periodoncia',
        'zona': 'encia',
        'zona_detalle': 'Encía y hueso de soporte',
        'orden': 6,
        'descripcion': (
            'Si sangra al cepillarte, no es normal. La encía sostiene el diente, y cuando '
            'se enferma el diente se afloja aunque esté sano.'
        ),
    },
    {
        'nombre': 'Odontopediatría',
        'zona': '',
        'zona_detalle': '',
        'orden': 7,
        'descripcion': 'Atención para niños, con el tiempo y la paciencia que eso requiere.',
    },
    {
        'nombre': 'Odontología bajo sedación',
        'zona': '',
        'zona_detalle': '',
        'orden': 8,
        'descripcion': 'Cualquiera de los tratamientos de arriba, si el miedo te lo impide.',
    },
]

# Lunes a viernes de 8 a 18, sábado de 8 a 14, domingo cerrado.
HORARIOS = [
    (0, time(8, 0), time(18, 0), False),
    (1, time(8, 0), time(18, 0), False),
    (2, time(8, 0), time(18, 0), False),
    (3, time(8, 0), time(18, 0), False),
    (4, time(8, 0), time(18, 0), False),
    (5, time(8, 0), time(14, 0), False),
    (6, None, None, True),
]

PRESENTACION = (
    'Consultorio de odontología general y todas las especialidades en Envigado. '
    'Lo que en otras partes se resuelve mandándote a tres sitios distintos, aquí se '
    'resuelve en el mismo consultorio y con el mismo equipo.\n\n'
    'Puedes ver casos, testimonios y cómo trabajamos en el día a día en Instagram.'
)


def cargar(apps, schema_editor):
    DatosClinica = apps.get_model('sitio', 'DatosClinica')
    Horario = apps.get_model('sitio', 'Horario')
    Tratamiento = apps.get_model('sitio', 'Tratamiento')

    DatosClinica.objects.update_or_create(
        pk=1,
        defaults={
            'nombre': 'Clínica Odontológica Dra. Paula Muñoz',
            'odontologa': 'Dra. Paula Muñoz',
            'direccion': 'Cra. 42 # 33 B Sur 93',
            'consultorio': 'Consultorio 207',
            'ciudad': 'Envigado',
            'departamento': 'Antioquia',
            'whatsapp': '573007711549',
            'telefono_fijo': '(604) 302 3308',
            'email': 'odontoestetic207@gmail.com',
            'instagram': 'https://www.instagram.com/paulamunozodontologa/',
            'facebook': 'https://www.facebook.com/Clinicapaulamunoz',
            'dominio': '',
            'presentacion': PRESENTACION,
        },
    )

    for dia, abre, cierra, cerrado in HORARIOS:
        Horario.objects.update_or_create(
            dia=dia,
            defaults={'abre': abre, 'cierra': cierra, 'cerrado': cerrado},
        )

    for datos in TRATAMIENTOS:
        Tratamiento.objects.update_or_create(nombre=datos['nombre'], defaults=datos)

    # Los testimonios no se siembran: solo hay uno verificado y el resto
    # deben salir de reseñas reales. Se cargan desde el administrador.


def descargar(apps, schema_editor):
    for modelo in ('Tratamiento', 'Horario', 'DatosClinica'):
        apps.get_model('sitio', modelo).objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [('sitio', '0001_initial')]

    operations = [migrations.RunPython(cargar, descargar)]
