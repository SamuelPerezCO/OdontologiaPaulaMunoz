from urllib.parse import quote

from .models import DatosClinica


def clinica(request):
    """Datos de contacto disponibles en cualquier plantilla.

    Se usan en la cabecera, el pie y el botón flotante, así que tenerlos
    aquí evita repetirlos en cada vista.
    """
    datos = DatosClinica.objects.first()
    if datos is None:
        return {'clinica': None, 'whatsapp_url': ''}

    saludo = quote('Hola, quiero agendar una cita')
    return {
        'clinica': datos,
        'whatsapp_url': f'https://wa.me/{datos.whatsapp}?text={saludo}',
    }
