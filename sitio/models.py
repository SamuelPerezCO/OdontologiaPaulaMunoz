from django.core.exceptions import ValidationError
from django.db import models


class Zona(models.TextChoices):
    """Zonas de la arcada que el odontograma sabe resaltar.

    Los valores coinciden con las claves de grupo de sitio/static/js/main.js.
    No son contenido editable: son anatomía, y cambiarlos rompería la
    relación entre el dibujo y la lista de tratamientos.
    """

    INCISIVOS = 'incisivos', 'Incisivos'
    CANINOS = 'caninos', 'Caninos'
    PREMOLARES = 'premolares', 'Premolares'
    MOLARES = 'molares', 'Molares'
    CORDALES = 'cordales', 'Cordales'
    ENCIA = 'encia', 'Encía'


# Numeración FDI de cada zona, de derecha a izquierda del paciente.
DIENTES_POR_ZONA = {
    Zona.INCISIVOS: [12, 11, 21, 22],
    Zona.CANINOS: [13, 23],
    Zona.PREMOLARES: [15, 14, 24, 25],
    Zona.MOLARES: [17, 16, 26, 27],
    Zona.CORDALES: [18, 28],
    Zona.ENCIA: [],
}


class DatosClinica(models.Model):
    """Datos de contacto de la clínica. Solo existe una fila."""

    nombre = models.CharField(
        'nombre', max_length=120, default='Clínica Odontológica Dra. Paula Muñoz')
    odontologa = models.CharField('odontóloga', max_length=120, default='Dra. Paula Muñoz')

    direccion = models.CharField('dirección', max_length=160)
    consultorio = models.CharField('consultorio', max_length=60, blank=True)
    ciudad = models.CharField('ciudad', max_length=80, default='Envigado')
    departamento = models.CharField('departamento', max_length=80, default='Antioquia')

    whatsapp = models.CharField(
        'WhatsApp', max_length=20,
        help_text='Solo dígitos, con indicativo del país. Ejemplo: 573007711549',
    )
    telefono_fijo = models.CharField('teléfono fijo', max_length=30, blank=True)
    email = models.EmailField('correo', blank=True)

    instagram = models.URLField('Instagram', blank=True)
    facebook = models.URLField('Facebook', blank=True)

    dominio = models.CharField(
        'dominio', max_length=120, blank=True,
        help_text='Dominio público, sin https://. Se usa en las etiquetas para buscadores.',
    )

    presentacion = models.TextField(
        'presentación', blank=True,
        help_text='Los párrafos de «La clínica». Separa cada párrafo con una línea en blanco.',
    )

    class Meta:
        verbose_name = 'datos de la clínica'
        verbose_name_plural = 'datos de la clínica'

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Los datos de la clínica no se pueden borrar.')

    @classmethod
    def cargar(cls):
        objeto, _ = cls.objects.get_or_create(pk=1)
        return objeto

    @property
    def direccion_completa(self):
        partes = [self.direccion, self.consultorio, f'{self.ciudad}, {self.departamento}']
        return ', '.join(p for p in partes if p)

    @property
    def whatsapp_legible(self):
        """573007711549 → +57 300 771 1549"""
        n = self.whatsapp
        if len(n) == 12 and n.startswith('57'):
            return f'+57 {n[2:5]} {n[5:8]} {n[8:]}'
        return f'+{n}'

    @property
    def parrafos_presentacion(self):
        return [p.strip() for p in self.presentacion.split('\n\n') if p.strip()]


class Horario(models.Model):
    """Un día de atención. La vista agrupa los días seguidos que coinciden."""

    DIAS = [
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'),
        (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo'),
    ]
    DIAS_SCHEMA = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                   'Friday', 'Saturday', 'Sunday']

    dia = models.PositiveSmallIntegerField('día', choices=DIAS, unique=True)
    abre = models.TimeField('abre', null=True, blank=True)
    cierra = models.TimeField('cierra', null=True, blank=True)
    cerrado = models.BooleanField('cerrado', default=False)

    class Meta:
        verbose_name = 'horario'
        verbose_name_plural = 'horarios'
        ordering = ['dia']

    def __str__(self):
        return f'{self.get_dia_display()}: {self.franja}'

    def clean(self):
        if not self.cerrado:
            if not self.abre or not self.cierra:
                raise ValidationError('Indica la hora de apertura y de cierre, o marca «cerrado».')
            if self.abre >= self.cierra:
                raise ValidationError('La hora de cierre debe ser posterior a la de apertura.')

    @staticmethod
    def _hhmm(t):
        # strftime('%-H') no existe en Windows, así que se arma a mano.
        return f'{t.hour}:{t.minute:02d}'

    @property
    def franja(self):
        if self.cerrado or not self.abre or not self.cierra:
            return 'Cerrado'
        return f'{self._hhmm(self.abre)} – {self._hhmm(self.cierra)}'

    @property
    def dia_schema(self):
        return self.DIAS_SCHEMA[self.dia]

    @property
    def clave_franja(self):
        """Dos días se agrupan si comparten esta clave."""
        if self.cerrado:
            return 'cerrado'
        return f'{self.abre}-{self.cierra}'


class TratamientoQuerySet(models.QuerySet):
    def publicados(self):
        return self.filter(publicado=True)

    def con_zona(self):
        return self.publicados().exclude(zona='')

    def sin_zona(self):
        return self.publicados().filter(zona='')


class Tratamiento(models.Model):
    nombre = models.CharField('nombre', max_length=120)
    zona = models.CharField(
        'zona de la arcada', max_length=20, choices=Zona.choices, blank=True,
        help_text='Déjalo en blanco si el tratamiento no se ubica en un diente '
                  '(odontopediatría, sedación). Cada zona admite un solo tratamiento.',
    )
    zona_detalle = models.CharField(
        'texto de la zona', max_length=80, blank=True,
        help_text='Lo que se lee bajo el nombre. Si se deja vacío, se usa el nombre de la zona.',
    )
    descripcion = models.TextField('descripción')
    orden = models.PositiveSmallIntegerField('orden', default=0)
    publicado = models.BooleanField('publicado', default=True)

    objects = TratamientoQuerySet.as_manager()

    class Meta:
        verbose_name = 'tratamiento'
        verbose_name_plural = 'tratamientos'
        ordering = ['orden', 'nombre']
        constraints = [
            models.UniqueConstraint(
                fields=['zona'],
                condition=~models.Q(zona=''),
                name='una_zona_un_tratamiento',
            ),
        ]

    def __str__(self):
        return self.nombre

    @property
    def dientes(self):
        return DIENTES_POR_ZONA.get(self.zona, [])

    @property
    def etiqueta_zona(self):
        return self.zona_detalle or self.get_zona_display()

    @property
    def ancla(self):
        return f'tx-{self.pk}'


class Testimonio(models.Model):
    texto = models.TextField('testimonio')
    autor = models.CharField(
        'autor', max_length=80, help_text='Como aparece en la reseña. Ejemplo: Juan T.')
    publicado = models.BooleanField('publicado', default=True)
    orden = models.PositiveSmallIntegerField('orden', default=0)

    class Meta:
        verbose_name = 'testimonio'
        verbose_name_plural = 'testimonios'
        ordering = ['orden', 'id']

    def __str__(self):
        return f'{self.autor}: {self.texto[:50]}'


class SolicitudCita(models.Model):
    """Lo que llega del formulario. No reemplaza al WhatsApp, lo acompaña."""

    nombre = models.CharField('nombre', max_length=120)
    telefono = models.CharField('teléfono', max_length=40)
    tratamiento = models.ForeignKey(
        Tratamiento, verbose_name='tratamiento', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='solicitudes',
    )
    mensaje = models.TextField('mensaje', blank=True)
    creada = models.DateTimeField('recibida', auto_now_add=True)
    atendida = models.BooleanField('atendida', default=False)

    class Meta:
        verbose_name = 'solicitud de cita'
        verbose_name_plural = 'solicitudes de cita'
        ordering = ['-creada']

    def __str__(self):
        return f'{self.nombre} — {self.creada:%d/%m/%Y %H:%M}'
