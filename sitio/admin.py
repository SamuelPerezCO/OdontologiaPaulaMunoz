from django.contrib import admin

from .models import DatosClinica, Horario, SolicitudCita, Tratamiento, Testimonio

admin.site.site_header = 'Clínica Dra. Paula Muñoz'
admin.site.site_title = 'Administración del sitio'
admin.site.index_title = 'Contenido del sitio'


@admin.register(DatosClinica)
class DatosClinicaAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Identidad', {'fields': ['nombre', 'odontologa', 'presentacion']}),
        ('Dónde queda', {'fields': ['direccion', 'consultorio', 'ciudad', 'departamento']}),
        ('Cómo contactar', {'fields': ['whatsapp', 'telefono_fijo', 'email']}),
        ('Redes y dominio', {'fields': ['instagram', 'facebook', 'dominio']}),
    ]

    def has_add_permission(self, request):
        # La fila se crea sola; no debe haber dos.
        return not DatosClinica.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ['dia_mostrado', 'franja_mostrada']
    ordering = ['dia']

    @admin.display(description='día', ordering='dia')
    def dia_mostrado(self, obj):
        return obj.get_dia_display()

    @admin.display(description='atención')
    def franja_mostrada(self, obj):
        return obj.franja


@admin.register(Tratamiento)
class TratamientoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'zona_mostrada', 'dientes_mostrados', 'orden', 'publicado']
    list_editable = ['orden', 'publicado']
    list_filter = ['publicado', 'zona']
    search_fields = ['nombre', 'descripcion']
    fields = ['nombre', 'zona', 'zona_detalle', 'descripcion', 'orden', 'publicado']

    @admin.display(description='zona')
    def zona_mostrada(self, obj):
        return obj.get_zona_display() if obj.zona else '— sin zona —'

    @admin.display(description='dientes')
    def dientes_mostrados(self, obj):
        if obj.zona and not obj.dientes:
            return 'Encía'
        return ', '.join(str(d) for d in obj.dientes) or '—'


@admin.register(Testimonio)
class TestimonioAdmin(admin.ModelAdmin):
    list_display = ['autor', 'resumen', 'orden', 'publicado']
    list_editable = ['orden', 'publicado']
    list_filter = ['publicado']

    @admin.display(description='testimonio')
    def resumen(self, obj):
        return obj.texto if len(obj.texto) <= 80 else obj.texto[:80] + '…'


@admin.register(SolicitudCita)
class SolicitudCitaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'tratamiento', 'creada', 'atendida']
    list_editable = ['atendida']
    list_filter = ['atendida', 'creada']
    search_fields = ['nombre', 'telefono', 'mensaje']
    readonly_fields = ['nombre', 'telefono', 'tratamiento', 'mensaje', 'creada']
    date_hierarchy = 'creada'

    def has_add_permission(self, request):
        # Las solicitudes solo entran por el formulario del sitio.
        return False
