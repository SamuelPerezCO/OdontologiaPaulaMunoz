# OdontologiaPaulaMunoz

Sitio web de la **Clínica Odontológica Dra. Paula Muñoz** — Envigado, Antioquia.

Proyecto Django. El contenido (tratamientos, horarios, testimonios, datos de
contacto) se edita desde el administrador, sin tocar código.

## Arrancar

```bash
python -m venv .venv
.venv\Scripts\activate        # en Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate       # deja el contenido real ya cargado
python manage.py createsuperuser
python manage.py runserver
```

El sitio queda en `http://127.0.0.1:8000/` y el administrador en
`http://127.0.0.1:8000/admin/`.

## Estructura

```
clinica/            Configuración del proyecto.
sitio/
  models.py         Datos de la clínica, horarios, tratamientos, testimonios,
                    solicitudes de cita.
  views.py          Página única, agrupación de horarios y ficha schema.org.
  forms.py          Formulario de cita, con campo trampa contra spam.
  admin.py          El administrador, en español.
  migrations/
    0002_…          Contenido real de la clínica como punto de partida.
  templates/sitio/  base.html e inicio.html.
  static/css        Estilos. La paleta vive en :root.
  static/js         Dibuja la arcada dental interactiva.
```

## La arcada

El elemento central es un odontograma de la arcada superior. Los dientes se
dibujan con sus medidas reales de corona en milímetros (ancho mesiodistal ×
altura) y se reparten sobre una elipse por longitud de arco. Cada corona se
traza con dos anchos, el del cuello y el del borde incisal, porque sobre una
curva el borde exterior recorre más arco que el interior: con un ancho único
quedaban huecos en cuña entre dientes vecinos.

Cada zona lleva a un tratamiento, y la relación es clínica, no decorativa:

| Zona | Tratamiento | Por qué ahí |
|------|-------------|-------------|
| Incisivos (12–22) | Blanqueamiento y diseño de sonrisa | Son los dientes que se ven al hablar |
| Caninos (13, 23) | Ortodoncia | El canino guía la mordida |
| Premolares (14–25) | Rehabilitación oral | Reparten la fuerza al masticar |
| Molares (16–27) | Limpieza dental | El sarro se acumula donde desemboca la glándula salival |
| Cordales (18, 28) | Cirugía maxilofacial | Muelas del juicio |
| Encía | Periodoncia | Sostiene el diente |

La numeración es FDI, la misma de la historia clínica.

Las zonas son anatomía, no contenido: viven en `Zona` y `DIENTES_POR_ZONA` en
`sitio/models.py`, y sus claves coinciden con las de `static/js/main.js`. Desde
el administrador se elige a qué zona corresponde cada tratamiento, pero no se
inventan zonas nuevas. Cada zona admite un solo tratamiento.

La arcada es un realce. Sin JavaScript, la lista de tratamientos sigue siendo
contenido real y legible, y los buscadores la indexan igual.

## Qué se edita desde el administrador

- **Datos de la clínica** — dirección, WhatsApp, correo, redes, presentación.
  Es una sola fila; no se puede borrar ni duplicar.
- **Horarios** — un día por fila. La página junta sola los días seguidos que
  comparten franja, así que lunes a viernes se lee en una línea.
- **Tratamientos** — nombre, descripción, zona y orden.
- **Testimonios** — solo salen los marcados como publicados.
- **Solicitudes de cita** — lo que llega del formulario, en solo lectura, con
  una casilla para marcar las ya atendidas.

## Pruebas

```bash
python manage.py test sitio
```

Cubren la agrupación de horarios, que la ficha schema.org sea JSON válido
(incluso con días cerrados o sin horarios), el filtrado de contenido no
publicado y el formulario de cita.

## Producción

Variables de entorno:

| Variable | Para qué |
|----------|----------|
| `DJANGO_SECRET_KEY` | Obligatoria. |
| `DJANGO_DEBUG` | `0` en producción. |
| `DJANGO_ALLOWED_HOSTS` | Dominios separados por coma. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Con esquema. Ejemplo: `https://midominio.com`. |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Aviso de solicitudes de cita. |
| `DJANGO_EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` para enviar de verdad. |

Con `DEBUG=0` los archivos estáticos se sirven con WhiteNoise, así que hay que
correr `collectstatic` antes de desplegar. La base por defecto es SQLite;
para varios usuarios editando conviene pasar a PostgreSQL.

## Pendiente

Cosas que necesitan material de la clínica:

- **Fotos.** Hoy no hay ninguna: el diseño se sostiene con tipografía y color.
  Faltan fotos del consultorio, del equipo y casos de antes/después.
- **Biografía de la Dra. Muñoz.** La presentación actual es genérica a
  propósito; hay que reemplazarla con formación y trayectoria reales desde el
  administrador.
- **Testimonios.** No se sembró ninguno: deben salir de reseñas reales de
  pacientes.
- **Dominio.** Falta cargarlo en los datos de la clínica.
