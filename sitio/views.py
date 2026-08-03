import json

from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe

from .forms import SolicitudCitaForm
from .models import DatosClinica, Horario, Testimonio, Tratamiento


def agrupar_horarios(horarios):
    """Junta los días seguidos que comparten franja.

    Lunes a viernes de 8 a 18 se lee como una línea, no como cinco.
    """
    grupos = []
    for horario in horarios:
        if grupos and grupos[-1]['clave'] == horario.clave_franja \
                and grupos[-1]['dias'][-1].dia == horario.dia - 1:
            grupos[-1]['dias'].append(horario)
        else:
            grupos.append({'clave': horario.clave_franja, 'dias': [horario]})

    for grupo in grupos:
        dias = grupo['dias']
        primero, ultimo = dias[0], dias[-1]
        # En español el segundo día va en minúscula: «Lunes a viernes».
        inicio_dia = primero.get_dia_display()
        fin_dia = ultimo.get_dia_display().lower()
        if len(dias) == 1:
            grupo['etiqueta'] = inicio_dia
        elif len(dias) == 2:
            grupo['etiqueta'] = f'{inicio_dia} y {fin_dia}'
        else:
            grupo['etiqueta'] = f'{inicio_dia} a {fin_dia}'
        grupo['franja'] = primero.franja
        grupo['cerrado'] = primero.cerrado
        grupo['dias_schema'] = [d.dia_schema for d in dias]
        grupo['abre'] = primero.abre
        grupo['cierra'] = primero.cierra
    return grupos


def avisar_solicitud(solicitud, datos):
    """Avisa por correo que llegó una solicitud.

    Si el correo falla no se interrumpe nada: la solicitud ya quedó
    guardada y visible en el administrador.
    """
    if not datos or not datos.email:
        return
    cuerpo = (
        f'Nombre: {solicitud.nombre}\n'
        f'Teléfono: {solicitud.telefono}\n'
        f'Tratamiento: {solicitud.tratamiento or "sin especificar"}\n\n'
        f'{solicitud.mensaje or "(sin mensaje)"}\n'
    )
    send_mail(
        subject=f'Solicitud de cita — {solicitud.nombre}',
        message=cuerpo,
        from_email=None,
        recipient_list=[datos.email],
        fail_silently=True,
    )


def datos_estructurados(request, datos, horarios, tratamientos):
    """schema.org/Dentist, para que la clínica aparezca bien en búsqueda local.

    Se arma en Python y no en la plantilla: encadenar comas con etiquetas
    {% if %} produce JSON inválido en cuanto un día está cerrado.
    """
    if datos is None:
        return ''

    ficha = {
        '@context': 'https://schema.org',
        '@type': 'Dentist',
        'name': datos.nombre,
        'description': 'Odontología general y todas las especialidades, '
                       'con opción de atención bajo sedación.',
        'url': request.build_absolute_uri(),
        'address': {
            '@type': 'PostalAddress',
            'streetAddress': ', '.join(p for p in [datos.direccion, datos.consultorio] if p),
            'addressLocality': datos.ciudad,
            'addressRegion': datos.departamento,
            'addressCountry': 'CO',
        },
    }

    if datos.telefono_fijo:
        ficha['telephone'] = datos.telefono_fijo
    if datos.email:
        ficha['email'] = datos.email

    redes = [u for u in (datos.instagram, datos.facebook) if u]
    if redes:
        ficha['sameAs'] = redes

    franjas = [
        {
            '@type': 'OpeningHoursSpecification',
            'dayOfWeek': grupo['dias_schema'],
            'opens': grupo['abre'].strftime('%H:%M'),
            'closes': grupo['cierra'].strftime('%H:%M'),
        }
        for grupo in horarios
        if not grupo['cerrado'] and grupo['abre'] and grupo['cierra']
    ]
    if franjas:
        ficha['openingHoursSpecification'] = franjas

    servicios = [{'@type': 'MedicalProcedure', 'name': t.nombre} for t in tratamientos]
    if servicios:
        ficha['availableService'] = servicios

    # ensure_ascii deja los acentos escapados y '<' no puede cerrar el <script>.
    return mark_safe(json.dumps(ficha, ensure_ascii=True).replace('<', '\\u003c'))


def inicio(request):
    datos = DatosClinica.objects.first()

    if request.method == 'POST':
        formulario = SolicitudCitaForm(request.POST)
        if formulario.is_valid():
            solicitud = formulario.save()
            avisar_solicitud(solicitud, datos)
            messages.success(
                request,
                'Recibimos tu solicitud. Te escribimos o te llamamos para confirmar la cita.',
            )
            return redirect(f'{request.path}#cita')
        messages.error(request, 'Revisa los datos: falta algo por corregir.')
    else:
        formulario = SolicitudCitaForm()

    horarios = agrupar_horarios(Horario.objects.all())
    publicados = list(Tratamiento.objects.publicados())

    contexto = {
        'tratamientos': [t for t in publicados if t.zona],
        'otros_tratamientos': [t for t in publicados if not t.zona],
        'testimonios': Testimonio.objects.filter(publicado=True),
        'horarios': horarios,
        'formulario': formulario,
        'ficha_json': datos_estructurados(request, datos, horarios, publicados),
    }
    return render(request, 'sitio/inicio.html', contexto)
